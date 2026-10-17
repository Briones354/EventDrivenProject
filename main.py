from js import document, lucide, window
import json

def get_cart():
    try:
        cart_json = window.localStorage.getItem("craveco_cart")
        if cart_json:
            return json.loads(str(cart_json))
    except Exception:
        pass
    return {}

def save_cart(cart):
    try:
        window.localStorage.setItem("craveco_cart", json.dumps(cart))
    except Exception:
        pass

def handle_login(event):
    email = document.getElementById("login-email").value.strip()
    password = document.getElementById("login-pass").value.strip()
    status_box = document.getElementById("status-output")

    if not email or not password:
        status_box.className = "status-box error"
        status_box.innerHTML = "⚠️ Please fill in all fields before signing in."
        return

    if "@" in email and len(password) >= 4:
        username = email.split('@')[0].capitalize()
        window.localStorage.setItem("craveco_user", username)
        window.location.href = "dashboard.html"
    else:
        status_box.className = "status-box error"
        status_box.innerHTML = "❌ Invalid credentials. Please check your email or password."

def toggle_password(event):
    pass_input = document.getElementById("login-pass")
    icon = document.getElementById("toggle-pass-icon")
    
    if pass_input and icon:
        if pass_input.type == "password":
            pass_input.type = "text"
            icon.setAttribute("data-lucide", "eye-off")
        else:
            pass_input.type = "password"
            icon.setAttribute("data-lucide", "eye")
        lucide.createIcons()

def handle_forgot_password(event):
    status_box = document.getElementById("status-output")
    if status_box:
        status_box.className = "status-box success"
        status_box.innerHTML = "🔄 Reset link sent! Check your inbox."

def handle_register(event):
    name = document.getElementById("reg-name").value.strip()
    email = document.getElementById("reg-email").value.strip()
    password = document.getElementById("reg-pass").value.strip()
    status_box = document.getElementById("reg-status-output")

    if not name or not email or not password:
        if status_box:
            status_box.className = "status-box error"
            status_box.innerHTML = "⚠️ Please complete all fields."
        return

    window.localStorage.setItem("craveco_user", name)
    window.location.href = "dashboard.html"

def open_card_options(event):
    btn = event.currentTarget
    card_id = btn.getAttribute("data-id")
    btn_container = document.getElementById(f"btn-container-{card_id}")
    options_container = document.getElementById(f"options-container-{card_id}")
    
    if btn_container and options_container:
        btn_container.classList.add("hidden")
        options_container.classList.remove("hidden")

def cancel_card_options(event):
    btn = event.currentTarget
    card_id = btn.getAttribute("data-id")
    btn_container = document.getElementById(f"btn-container-{card_id}")
    options_container = document.getElementById(f"options-container-{card_id}")
    
    if btn_container and options_container:
        options_container.classList.add("hidden")
        btn_container.classList.remove("hidden")

def confirm_card_order(event):
    btn = event.currentTarget
    card_id = btn.getAttribute("data-id")
    item_name = btn.getAttribute("data-item")
    item_price = btn.getAttribute("data-price")
    
    pay_select = document.getElementById(f"pay-{card_id}")
    note_input = document.getElementById(f"note-{card_id}")
    
    payment = pay_select.value if pay_select else "COD"
    notes = note_input.value.strip() if note_input else "None"
    if not notes:
        notes = "None"

    order_summary = {
        "name": item_name,
        "price": item_price,
        "payment": payment,
        "notes": notes
    }
    window.localStorage.setItem("craveco_last_order", json.dumps(order_summary))
    window.location.href = "order_success.html"

def add_to_cart(event):
    btn = event.currentTarget
    item_name = btn.getAttribute("data-item")
    
    price_attr = btn.getAttribute("data-price")
    if price_attr:
        item_price = int(price_attr)
    else:
        item_price = 199 

    cart = get_cart()
    if item_name in cart:
        cart[item_name]["qty"] += 1
    else:
        cart[item_name] = {"price": item_price, "qty": 1, "selected": True}

    save_cart(cart)
    update_cart_badge()
    render_cart_items()

def increase_qty(event):
    btn = event.currentTarget
    item_name = btn.getAttribute("data-item")

    cart = get_cart()
    if item_name in cart:
        cart[item_name]["qty"] += 1

    save_cart(cart)
    update_cart_badge()
    render_cart_items()

def decrease_qty(event):
    btn = event.currentTarget
    item_name = btn.getAttribute("data-item")

    cart = get_cart()
    if item_name in cart:
        if cart[item_name]["qty"] > 1:
            cart[item_name]["qty"] -= 1
        else:
            del cart[item_name] 

    save_cart(cart)
    update_cart_badge()
    render_cart_items()

def remove_from_cart(event):
    btn = event.currentTarget
    item_name = btn.getAttribute("data-item")

    cart = get_cart()
    if item_name in cart:
        del cart[item_name]

    save_cart(cart)
    update_cart_badge()
    render_cart_items()

def toggle_item_selection(event):
    checkbox = event.currentTarget
    item_name = checkbox.getAttribute("data-item")
    is_checked = checkbox.checked

    cart = get_cart()
    if item_name in cart:
        cart[item_name]["selected"] = is_checked

    save_cart(cart)
    update_total_price(cart)

def update_cart_badge():
    cart = get_cart()
    total_qty = sum(item["qty"] for item in cart.values())
    badge = document.getElementById("cart-badge-count")
    if badge:
        badge.innerHTML = str(total_qty)

def update_total_price(cart):
    total_price = 0
    for name, data in cart.items():
        if data.get("selected", True):
            total_price += data["price"] * data["qty"]
    
    total_price_el = document.getElementById("cart-total-price")
    if total_price_el:
        total_price_el.innerHTML = f"₱{total_price}"

def render_cart_items():
    container = document.getElementById("cart-items-list")
    
    if not container:
        return

    cart = get_cart()
    if not cart:
        container.innerHTML = "<p style='color: var(--text-muted); font-size: 13px; text-align: center; padding: 15px;'>Your cart is empty.</p>"
        total_price_el = document.getElementById("cart-total-price")
        if total_price_el:
            total_price_el.innerHTML = "₱0"
        return

    html_content = ""

    for name, data in cart.items():
        subtotal = data["price"] * data["qty"]
        is_selected = "checked" if data.get("selected", True) else ""
        html_content += f"""
            <div style="background: var(--input-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 8px 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <input type="checkbox" {is_selected} py-change="toggle_item_selection" data-item="{name}" style="accent-color: var(--brand-orange); width: 16px; height: 16px; cursor: pointer;">
                    <div>
                        <div style="font-size: 12px; font-weight: 700;">{name}</div>
                        <div style="font-size: 10px; color: var(--text-muted);">₱{data['price']} x {data['qty']} = <span style="color: var(--brand-orange);">₱{subtotal}</span></div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <button class="qty-btn" py-click="decrease_qty" data-item="{name}">-</button>
                        <span style="font-size: 12px; font-weight: 700; color: var(--brand-white); width: 16px; text-align: center;">{data['qty']}</span>
                        <button class="qty-btn" py-click="increase_qty" data-item="{name}">+</button>
                    </div>
                    <button class="delete-btn" py-click="remove_from_cart" data-item="{name}">Delete</button>
                </div>
            </div>
        """

    container.innerHTML = html_content
    update_total_price(cart)

def confirm_cart_checkout(event):
    cart = get_cart()
    if not cart:
        return

    selected_items = {name: data for name, data in cart.items() if data.get("selected", True)}
    
    if not selected_items:
        return

    payment_el = document.getElementById("cart-payment-method")
    notes_el = document.getElementById("cart-notes")

    payment = payment_el.value if payment_el else "COD"
    notes = notes_el.value.strip() if notes_el else "None"
    if not notes:
        notes = "None"

    item_names = ", ".join([f"{name} (x{data['qty']})" for name, data in selected_items.items()])
    total_price = sum(data["price"] * data["qty"] for data in selected_items.values())

    order_summary = {
        "name": item_names,
        "price": f"₱{total_price}",
        "payment": payment,
        "notes": notes
    }
    window.localStorage.setItem("craveco_last_order", json.dumps(order_summary))
    
    for name in selected_items:
        del cart[name]
    save_cart(cart)
    
    update_cart_badge()
    window.location.href = "order_success.html"

update_cart_badge()
render_cart_items()