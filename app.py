import os
import mysql.connector
from mysql.connector import errors
from flask import Flask, request, jsonify, session, send_from_directory, abort, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-long-random-string")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

PUBLIC_FILES = {
    "index.html",
    "register.html",
    "dashboard.html",
    "cart.html",
    "order_success.html",
    "main.py",
    "logo.png",
    "promo.mp4",
}

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "craveco"),
}

PAYMENT_METHODS = {"COD", "GCash", "Card"}


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def clean(value, limit):
    return (value or "").strip()[:limit]



@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def public_file(filename):
    if filename not in PUBLIC_FILES:
        abort(404)
    return send_from_directory(BASE_DIR, filename)



@app.post("/api/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    name = clean(data.get("name"), 100)
    email = clean(data.get("email"), 150).lower()
    password = data.get("password") or ""

    if not name or "@" not in email or len(password) < 6:
        return jsonify(error="Enter your name, a valid email, and a password of at least 6 characters."), 400

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
    except errors.IntegrityError:
        return jsonify(error="An account with this email already exists."), 400

    return jsonify(message="Account created successfully."), 201  

@app.post("/api/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = clean(data.get("email"), 150).lower()
    password = data.get("password") or ""

    cur = get_db().cursor(dictionary=True)
    cur.execute("SELECT id, name, password_hash FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify(error="Wrong email or password. Check both and try again."), 401

    session["user_id"] = user["id"]
    return jsonify(name=user["name"])


@app.get("/api/me")
def me():
    if "user_id" not in session:
        return jsonify(error="Not signed in."), 401

    cur = get_db().cursor(dictionary=True)
    cur.execute("SELECT name FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    if not user:
        session.clear()
        return jsonify(error="Not signed in."), 401
    return jsonify(name=user["name"])


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.post("/api/orders")
def create_order():
    if "user_id" not in session:
        return jsonify(error="Please sign in to place an order."), 401

    data = request.get_json(force=True, silent=True) or {}
    payment = data.get("payment", "COD")
    phone = clean(data.get("phone"), 30)
    address = clean(data.get("address"), 255)
    notes = clean(data.get("notes"), 255)

    if payment not in PAYMENT_METHODS:
        return jsonify(error="Choose a valid payment method."), 400
    if sum(ch.isdigit() for ch in phone) < 7 or len(address) < 5:
        return jsonify(error="Enter a contact number and a delivery address."), 400

    qty_by_name = {}
    for item in data.get("items") or []:
        try:
            name = str(item["name"])
            qty = int(item["qty"])
        except (KeyError, TypeError, ValueError):
            return jsonify(error="Some items in your order are invalid."), 400
        if not 1 <= qty <= 50:
            return jsonify(error="Quantity must be between 1 and 50."), 400
        qty_by_name[name] = qty_by_name.get(name, 0) + qty

    if not qty_by_name:
        return jsonify(error="Your cart is empty."), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(qty_by_name))
    cur.execute(
        f"SELECT name, price FROM menu_items WHERE is_available = 1 AND name IN ({placeholders})",
        tuple(qty_by_name),
    )
    prices = {row["name"]: row["price"] for row in cur.fetchall()}

    unavailable = [n for n in qty_by_name if n not in prices]
    if unavailable:
        return jsonify(error="No longer available: " + ", ".join(unavailable)), 400

    lines = [{"name": n, "price": prices[n], "qty": q} for n, q in qty_by_name.items()]
    total = sum(line["price"] * line["qty"] for line in lines)

    try:
        write_cur = db.cursor()
        write_cur.execute(
            "INSERT INTO orders (user_id, payment_method, phone, address, notes, total) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (session["user_id"], payment, phone, address, notes, total),
        )
        order_id = write_cur.lastrowid
        write_cur.executemany(
            "INSERT INTO order_items (order_id, item_name, price, qty) VALUES (%s, %s, %s, %s)",
            [(order_id, l["name"], l["price"], l["qty"]) for l in lines],
        )
        db.commit()  
    except Exception:
        db.rollback()
        return jsonify(error="We couldn't save your order. Please try again."), 500

    return jsonify(order_id=order_id, total=total, items=lines)


@app.get("/api/orders")
def my_orders():
    if "user_id" not in session:
        return jsonify(error="Please sign in first."), 401

    cur = get_db().cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", (session["user_id"],)
    )
    orders = cur.fetchall()

    for order in orders:
        cur.execute(
            "SELECT item_name, price, qty FROM order_items WHERE order_id = %s", (order["id"],)
        )
        order["items"] = cur.fetchall()
        order["created_at"] = str(order["created_at"])

    return jsonify(orders)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
