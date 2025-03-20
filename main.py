from webpy import WebPy
from broadcast import Request, Response
from blueprint import Blueprint
from sessions import Sessions
from middleware import Middleware

# Initialize the WebPy application
app = WebPy()

# Initialize middleware
middleware = Middleware(app)

# Initialize sessions
sessions = Sessions()


# ----------------------
# Middleware definitions
# ----------------------


@middleware.enroll
def request_logger(request: Request, response: Response) -> None:
    """Log information about incoming requests."""
    address = request.headers.get("X-Forwarded-For", "Unknown")
    print(f"Request from {address} to {request.path} [{request.method}]")


@middleware.enroll
def session_tracker(request: Request, response: Response) -> None:
    """Track session activity."""
    session_id = sessions.get("session_id", None)
    if session_id:
        print(f"Active session: {session_id}")
    else:
        print("No active session")


# ----------------------
# Basic route handlers
# ----------------------


@app.route("/")
def home(request: Request, response: Response) -> None:
    """Render the homepage with a template."""
    context = {
        "title": "WebPy Demo",
        "name": "Guest",
        "messages": ["Welcome to the WebPy demo!", "Explore our features!"],
    }

    # Get username from session if available
    username = sessions.get("username", None)
    if username:
        context["name"] = username

    html = app.render("index.html", **context)
    response.headers["Content-Type"] = "text/html"
    response.body = html.encode("utf-8")


@app.route("/api/test", methods=["GET", "POST"])
def test_api(request: Request, response: Response) -> None:
    """Handle basic API requests."""
    if request.method == "GET":
        page = request.queries.get("page", ["1"])[0]
        response.json({"method": "GET", "page": page, "status": "success"})
    elif request.method == "POST":
        data = request.json()
        response.json({"method": "POST", "received": data, "status": "success"})


@app.route("/users/<id:int>")
def get_user(request: Request, response: Response, id: int) -> None:
    """Handle dynamic route with user ID."""
    response.json({"user_id": id, "name": f"User {id}"})


# ----------------------
# Session management
# ----------------------


@app.route("/login", methods=["GET", "POST"])
def login(request: Request, response: Response) -> None:
    """Handle user login."""
    if request.method == "GET":
        html = app.render("login.html", title="Login")
        response.headers["Content-Type"] = "text/html"
        response.body = html.encode("utf-8")
    elif request.method == "POST":
        ...

@app.route("/logout")
def logout(request: Request, response: Response) -> None:
    """Handle user logout."""
    username = sessions.get("username", "Guest")
    sessions.remove("username")
    sessions.remove("session_id")

    response.json({"status": "success", "message": f"Goodbye, {username}!"})


@app.route("/profile")
def profile(request: Request, response: Response) -> None:
    """Display user profile information."""
    username = sessions.get("username", None)

    if not username:
        # Redirect to login if no session
        response.redirect("/login")
        return

    # In a real app, you would fetch user data here
    user_data = {
        "username": username,
        "email": f"{username.lower()}@example.com",
        "joined": "2025-01-01",
    }

    html = app.render("profile.html", title="Profile", user=user_data)
    response.headers["Content-Type"] = "text/html"
    response.body = html.encode("utf-8")


# ----------------------
# Static file serving
# ----------------------


@app.route("/static/<path:path>")
def static_files(request: Request, response: Response, path: str) -> None:
    """Serve static files."""
    # In a real app, WebPy would handle this automatically
    # This is just for demonstration
    content_type = "text/plain"
    if path.endswith(".css"):
        content_type = "text/css"
    elif path.endswith(".js"):
        content_type = "application/javascript"
    elif path.endswith(".png"):
        content_type = "image/png"
    elif path.endswith(".jpg"):
        content_type = "image/jpeg"

    response.headers["Content-Type"] = content_type
    # In a real app, you would actually read the file here
    response.body = f"Content of {path}".encode("utf-8")


# ----------------------
# Blueprints for modular organization
# ----------------------

# Create a blueprint for admin routes
admin = Blueprint("admin", prefix="/admin")


@admin.route("/dashboard")
def admin_dashboard(request: Request, response: Response) -> None:
    """Display admin dashboard."""
    # Check if user is an admin
    username = sessions.get("username", None)
    if not username or username != "admin":
        response.status = 403
        response.json({"error": "Forbidden", "message": "Admin access required"})
        return

    # In a real app, you would fetch admin data here
    stats = {"users": 1250, "posts": 347, "comments": 1893}

    html = app.render("admin/dashboard.html", title="Admin Dashboard", stats=stats)
    response.headers["Content-Type"] = "text/html"
    response.body = html.encode("utf-8")


@admin.route("/users")
def admin_users(request: Request, response: Response) -> None:
    """Display user management page."""
    # Check if user is an admin
    username = sessions.get("username", None)
    if not username or username != "admin":
        response.status = 403
        response.json({"error": "Forbidden", "message": "Admin access required"})
        return

    # In a real app, you would fetch user data here
    users = [
        {"id": 1, "username": "user1", "email": "user1@example.com"},
        {"id": 2, "username": "user2", "email": "user2@example.com"},
        {"id": 3, "username": "user3", "email": "user3@example.com"},
    ]

    html = app.render("admin/users.html", title="User Management", users=users)
    response.headers["Content-Type"] = "text/html"
    response.body = html.encode("utf-8")


# Create a blueprint for API routes
api = Blueprint("api", prefix="/api/v1")


@api.route("/users", methods=["GET", "POST"])
def api_users(request: Request, response: Response) -> None:
    """RESTful API endpoint for user management."""
    if request.method == "GET":
        # In a real app, you would fetch user data here
        users = [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"},
            {"id": 3, "username": "user3"},
        ]
        response.json({"users": users})
    elif request.method == "POST":
        a = request.json()
        # In a real app, you would validate and save the data
        response.status = 201
        response.json({"status": "success", "message": "User created"})


@api.route("/users/<id:int>", methods=["GET", "PUT", "DELETE"])
def api_user(request: Request, response: Response, id: int) -> None:
    """RESTful API endpoint for individual user management."""
    # In a real app, you would fetch user data here
    user = {"id": id, "username": f"user{id}", "email": f"user{id}@example.com"}

    if request.method == "GET":
        response.json({"user": user})
    elif request.method == "PUT":
        data = request.json()
        # In a real app, you would validate and update the user
        response.json(
            {"status": "success", "message": "User updated", "user": {**user, **data}}
        )
    elif request.method == "DELETE":
        # In a real app, you would delete the user
        response.status = 204
        response.body = b""


# ----------------------
# Error handling
# ----------------------


@app.error(404)
def not_found(request: Request, response: Response) -> None:
    """Custom handler for 404 Not Found errors."""
    response.status = 404

    # Check if the request accepts JSON
    accept = request.headers.get("Accept", "")
    if "application/json" in accept:
        response.json({"error": "Not Found", "path": request.path})
    else:
        html = app.render("errors/404.html", title="Not Found", path=request.path)
        response.headers["Content-Type"] = "text/html"
        response.body = html.encode("utf-8")


@app.error(500)
def server_error(request: Request, response: Response) -> None:
    """Custom handler for 500 Internal Server Error."""
    response.status = 500


# ----------------------
# Route excluded from middleware
# ----------------------


@app.route("/api/health")
@middleware.exclude
def health_check(request: Request, response: Response) -> None:
    """Health check endpoint without middleware."""
    response.json({"status": "healthy", "version": "1.0.0"})


# ----------------------
# Main function to run the server
# ----------------------


def main() -> None:
    """Start the WebPy server."""
    # For development
    app.run(ip="127.0.0.1", port=8000)

    # For production with HTTPS
    # app.run(
    #     ip="0.0.0.0",
    #     port=443,
    #     certfile='path/to/cert.pem',
    #     keyfile='path/to/key.pem'
    # )


if __name__ == "__main__":
    main()
