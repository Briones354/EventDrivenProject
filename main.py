import json
from js import document, window, lucide
from pyodide.http import pyfetch

async def api_post(endpoint, payload):
    response = await pyfetch(
        endpoint,
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps(payload),
    )

    content_type = response.headers.get("content-type", "")

    if "application/json" not in content_type:
        body_text = await response.text()
        raise Exception(
            f"Expected JSON but received {content_type}. "
            f"Response: {body_text[:300]}"
        )

    result = await response.json()
    return response, result


async def handle_login(event):
    email = document.getElementById("login-email").value.strip().lower()
    password = document.getElementById("login-pass").value
    status_box = document.getElementById("status-output")

    if not email or not password:
        status_box.className = "status-box error"
        status_box.textContent = "Please enter your email and password."
        return

    try:
        response, result = await api_post(
            "/api/login",
            {
                "email": email,
                "password": password,
            },
        )

        if not response.ok:
            status_box.className = "status-box error"
            status_box.textContent = result.get(
                "error", "Invalid email or password."
            )
            return

        status_box.className = "status-box success"
        status_box.textContent = "Login successful!"

        window.location.href = "dashboard.html"

    except Exception as e:
        status_box.className = "status-box error"
        status_box.textContent = f"Login error: {str(e)}"
        print("Login error:", str(e))


async def handle_register(event):
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

    try:
        response, result = await api_post(
            "/api/register",
            {
                "name": name,
                "email": email,
                "password": password,
            },
        )

        if not response.ok:
            status_box.className = "status-box error"
            status_box.textContent = result.get(
                "error", "Registration failed."
            )
            return

        status_box.className = "status-box success"
        status_box.textContent = (
            "Account created successfully! Please sign in."
        )

        window.location.href = "index.html"

    except Exception as e:
        status_box.className = "status-box error"
        status_box.textContent = f"Registration error: {str(e)}"
        print("Registration error:", str(e))


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
        status_box.className = "status-box error"
        status_box.textContent = (
            "Password reset is not configured yet. "
            "Please contact the administrator."
        )
