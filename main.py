import json
from js import document, window, lucide, Object
from pyodide.ffi import create_proxy

def get_cart():
    cart_json = window.localStorage.getItem("craveco_cart")
    if not cart_json:
        return []
    try:
        data = json.loads(cart_json)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []

def save_cart(cart_list):
    window.localStorage.setItem("craveco_cart", json.dumps(cart_list))
    update_cart_badge()

def get_users():
    users_json = window.localStorage.getItem("craveco_users")
    if not users_json:
        return {}
    try:
        data = json.loads(users_json)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}

def save_users(users_dict):
    window.localStorage.setItem("craveco_users", json.dumps(users_dict))

def update_cart_badge():
    badge = document.getElementById("cart-badge-count") or document.getElementById("cart-count")
    if badge:
        cart = get_cart()
        total_items = sum(item.get("qty", 1) for item in cart if isinstance(item, dict))
        badge.textContent = str(total_items)

def handle_login(event):
    email_elem = document.getElementById("login-email")
    pass_elem = document.getElementById("login-pass")
    status_box = document.getElementById("status-output")

    if not email_elem or not pass_elem:
        return

    email = email_elem.value.strip().lower()
    password = pass_elem.value

    if not email or not password:
        status_box.className = "status-box error"
        status_box.textContent = "Please enter your email and password."
        return

    users = get_users()

    if email not in users or users[email].get("password") != password:
        status_box.className = "status-box error"
        status_box.textContent = "Invalid email or password."
        return

    status_box.className = "status-box success"
    status_box.textContent = "Login successful! Redirecting..."
    
    window.localStorage.setItem("craveco_current_user", json.dumps(users[email]))
    window.location.href = "dashboard.html"

def handle_register(event):
    name_elem = document.getElementById("reg-name")
    email_elem = document.getElementById("reg-email")
    pass_elem = document.getElementById("reg-pass")
    status_box = document.getElementById("reg-status-output")

    if not name_elem or not email_elem or not pass_elem:
        return

    name = name_elem.value.strip()
    email = email_elem.value.strip().lower()
    password = pass_elem.value

    if not name or not email or not password:
        status_box.className = "status-box error"
        status_box.textContent = "Please complete all fields."
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        status_box.className = "status-box error"
        status_box.textContent = "Please enter a valid email address."
        return

    if len(password) < 6:
        status_box.className = "status-box error"
        status_box.textContent = "Password must be at least 6 characters."
        return

    users = get_users()

    if email in users:
        status_box.className = "status-box error"
        status_box.textContent = "An account with this email already exists."
        return

    users[email] = {
        "name": name,
        "email": email,
        "password": password
    }
    
    save_users(users)

    status_box.className = "status-box success"
    status_box.textContent = "Account created successfully! Switching..."

    window.location.href = "index.html"

def toggle_password(event):
    pass_input = document.getElementById("login-pass") or document.getElementById("reg-pass")
    icon = document.getElementById("toggle-pass-icon")

    if pass_input and icon:
        if pass_input.type == "password":
            pass_input.type = "text"
            icon.setAttribute("data-lucide", "eye-off")
        else:
            pass_input.type = "password"
            icon.setAttribute("data-lucide", "eye")

        if hasattr(lucide, "createIcons"):
            lucide.createIcons()

def handle_forgot_password(event):
    status_box = document.getElementById("status-output")
    if status_box:
        status_box.className = "status-box error"
        status_box.textContent = "Password reset is not configured yet. Please contact support."

# Dashboard Card Interaction Handlers (Missing previously)
def open_card_options(event):
    target = getattr(event, "currentTarget", None) or getattr(event, "target", None)
    if not target:
        return
    card_id = target.getAttribute("data-id")
    if not card_id:
        return
    
    btn_container = document.getElementById(f"btn-container-{card_id}")
    options_container = document.getElementById(f"options-container-{card_id}")
    
    if btn_container and options_container:
        btn_container.classList.add("hidden")
        options_container.classList.remove("hidden")

def cancel_card_options(event):
    target = getattr(event, "currentTarget", None) or getattr(event, "target", None)
    if not target:
        return
    card_id = target.getAttribute("data-id")
    if not card_id:
        return
    
    btn_container = document.getElementById(f"btn-container-{card_id}")
    options_container = document.getElementById(f"options-container-{card_id}")
    
    if btn_container and options_container:
        options_container.classList.add("hidden")
        btn_container.classList.remove("hidden")

def confirm_card_order(event):
    target = getattr(event, "currentTarget", None) or getattr(event, "target", None)
    if not target:
        return
    card_id = target.getAttribute("data-id")
    item_name = target.getAttribute("data-item")
    price_str = target.getAttribute("data-price")
    
    if not card_id:
        return

    phone_elem = document.getElementById(f"phone-{card_id}")
    address_elem = document.getElementById(f"address-{card_id}")
    pay_elem = document.getElementById(f"pay-{card_id}")
    note_elem = document.getElementById(f"note-{card_id}")

    phone = phone_elem.value.strip() if phone_elem else ""
    address = address_elem.value.strip() if address_elem else ""
    payment = pay_elem.value if pay_elem else "COD"
    notes = note_elem.value.strip() if note_elem else "None"

    if not phone or not address:
        window.alert("Please provide your contact number and delivery address.")
        return

    try:
        clean_price = float(price_str.replace("₱", "").replace(",", "").strip())
    except Exception:
        clean_price = 0.0

    order_data = {
        "name": item_name,
        "price": f"₱{int(clean_price)}",
        "payment": payment,
        "notes": notes if notes else "None"
    }
    
    window.localStorage.setItem("craveco_last_order", json.dumps(order_data))
    window.location.href = "order_success.html"

def add_to_cart(event):
    try:
        target = getattr(event, "currentTarget", None) or getattr(event, "target", None)
        if not target:
            return

        item_name = target.getAttribute("data-item")
        price_str = target.getAttribute("data-price")

        if not item_name:
            return

        price_val = float(price_str) if price_str else 0.0

        cart = get_cart()
        found = False
        for item in cart:
            if isinstance(item, dict) and item.get("name") == item_name:
                item["qty"] = int(item.get("qty", 1)) + 1
                found = True
                break

        if not found:
            cart.append({
                "name": item_name,
                "price": price_val,
                "qty": 1
            })

        save_cart(cart)
        window.alert(f"{item_name} added to cart!")
    except Exception as e:
        print("Error in add_to_cart:", e)

def change_qty(item_name, delta):
    cart = get_cart()
    new_cart = []

    for item in cart:
        if isinstance(item, dict):
            if item.get("name") == item_name:
                item["qty"] = int(item.get("qty", 1)) + delta
                if item["qty"] > 0:
                    new_cart.append(item)
            else:
                new_cart.append(item)

    save_cart(new_cart)
    render_cart_items()

def remove_item(item_name):
    cart = get_cart()
    new_cart = [item for item in cart if isinstance(item, dict) and item.get("name") != item_name]
    save_cart(new_cart)
    render_cart_items()

def render_cart_items():
    container = document.getElementById("cart-items-list")
    total_elem = document.getElementById("cart-total-price")

    if not container:
        return

    cart = get_cart()
    container.innerHTML = ""
    total_amount = 0

    if not cart:
        container.innerHTML = '<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:10px;">Your cart is empty.</div>'
        if total_elem:
            total_elem.textContent = "₱0"
        return

    for item in cart:
        if not isinstance(item, dict):
            continue
            
        name = item.get("name", "Item")
        price = float(item.get("price", 0))
        qty = int(item.get("qty", 1))
        item_total = price * qty
        total_amount += item_total

        row = document.createElement("div")
        row.style.cssText = (
            "background: var(--input-bg); border: 1px solid var(--border-color); "
            "border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; "
            "display: flex; justify-content: space-between; align-items: center; gap: 8px;"
        )

        info_div = document.createElement("div")
        info_div.innerHTML = f'<div style="font-size:12px; font-weight:700;">{name}</div>' \
                             f'<div style="font-size:11px; color:var(--text-muted);">₱{int(price)} x {qty} = ₱{int(item_total)}</div>'

        actions_div = document.createElement("div")
        actions_div.style.cssText = "display: flex; align-items: center; gap: 6px;"

        btn_minus = document.createElement("button")
        btn_minus.className = "qty-btn"
        btn_minus.textContent = "-"
        btn_minus.addEventListener("click", create_proxy(lambda e, n=name: change_qty(n, -1)))

        qty_span = document.createElement("span")
        qty_span.style.cssText = "font-size: 12px; font-weight: 700; min-width: 16px; text-align: center;"
        qty_span.textContent = str(qty)

        btn_plus = document.createElement("button")
        btn_plus.className = "qty-btn"
        btn_plus.textContent = "+"
        btn_plus.addEventListener("click", create_proxy(lambda e, n=name: change_qty(n, 1)))

        btn_del = document.createElement("button")
        btn_del.className = "delete-btn"
        btn_del.textContent = "✕"
        btn_del.addEventListener("click", create_proxy(lambda e, n=name: remove_item(n)))

        actions_div.appendChild(btn_minus)
        actions_div.appendChild(qty_span)
        actions_div.appendChild(btn_plus)
        actions_div.appendChild(btn_del)

        row.appendChild(info_div)
        row.appendChild(actions_div)
        container.appendChild(row)

    if total_elem:
        total_elem.textContent = f"₱{int(total_amount)}"

def confirm_cart_checkout(event):
    cart = get_cart()
    if not cart:
        window.alert("Your cart is empty! Add items before checking out.")
        return

    phone_elem = document.getElementById("cart-phone")
    address_elem = document.getElementById("cart-address")

    phone = phone_elem.value.strip() if phone_elem else ""
    address = address_elem.value.strip() if address_elem else ""

    if not phone or not address:
        window.alert("Please fill in your Contact Number and Delivery Address.")
        return

    first_item = cart[0] if cart else {"name": "CraveCo Order", "price": 0}
    total_val = sum(item.get("price", 0) * item.get("qty", 1) for item in cart)

    order_data = {
        "name": f"{first_item.get('name')} (+{len(cart)-1} more)" if len(cart) > 1 else first_item.get('name'),
        "price": f"₱{int(total_val)}",
        "payment": document.getElementById("cart-payment-method").value if document.getElementById("cart-payment-method") else "COD",
        "notes": document.getElementById("cart-notes").value if document.getElementById("cart-notes") else "None"
    }

    window.localStorage.setItem("craveco_last_order", json.dumps(order_data))
    save_cart([])
    window.location.href = "order_success.html"

update_cart_badge()
render_cart_items()