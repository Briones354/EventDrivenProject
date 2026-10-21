import json
from js import document, window, lucide

def get_users():
    users_json = window.localStorage.getItem("craveco_users")
    if not users_json:
        return {}
    return json.loads(users_json)

def save_users(users_dict):
    window.localStorage.setItem("craveco_users", json.dumps(users_dict))


def handle_login(event):
    email = document.getElementById("login-email").value.strip().lower()
    password = document.getElementById("login-pass").value
    status_box = document.getElementById("status-output")

    if not email or not password:
        status_box.className = "status-box error"
        status_box.textContent = "Please enter your email and password."
        return

    users = get_users()

    if email not in users or users[email]["password"] != password:
        status_box.className = "status-box error"
        status_box.textContent = "Invalid email or password."
        return

    status_box.className = "status-box success"
    status_box.textContent = "Login successful! Redirecting..."
    
    # Save active session user and redirect
    window.localStorage.setItem("craveco_current_user", json.dumps(users[email]))
    window.location.href = "dashboard.html"


def handle_register(event):
    name = document.getElementById("reg-name").value.strip()
    email = document.getElementById("reg-email").value.strip().lower()
    password = document.getElementById("reg-pass").value
    status_box = document.getElementById("reg-status-output")

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
    status_box.textContent = "Account created successfully! Redirecting to sign in..."
    
    # Redirect to index after successful registration
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

        lucide.createIcons()


def handle_forgot_password(event):
    status_box = document.getElementById("status-output")
    if status_box:
        status_box.className = "status-box error"
        status_box.textContent = (
            "Password reset is not configured yet. "
            "Please contact the administrator."
        )