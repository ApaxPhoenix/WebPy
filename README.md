# WebPy

WebPy is a lightweight and intuitive Python framework designed to simplify web development. Whether you're building a small web application or a complex API, WebPy provides the tools you need to get the job done efficiently and effectively.

## 🚀 Core Features

WebPy comes packed with features to make web development straightforward and enjoyable:

| Feature                | Description                                             |
|------------------------|---------------------------------------------------------|
| Fast HTTP Handling     | Efficiently manage HTTP requests and responses.         |
| Intelligent Routing    | Define routes with ease and flexibility.               |
| Jinja2 Templates       | Create dynamic and reusable HTML templates.            |
| Static File Serving    | Serve static files like CSS, JavaScript, and images.   |
| WebSocket Support      | Build real-time applications with WebSocket.           |
| Session Management     | Handle user sessions securely and simply.              |
| HTTPS Support          | Secure your application with built-in HTTPS.           |
| Error Handling         | Define custom error pages and responses.               |
| Authentication Support | Basic, JWT, and OAuth integrations.                    |
| Role-Based Access      | Control access to routes based on user roles.          |
| CSRF Protection        | Protect your application from Cross-Site Request Forgery attacks. |
| Blueprint System       | Organize your application into modular components.     |

## 🏗️ Project Structure

To keep your application organized, we suggest the following structure:

```
project/
├── static/          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/       # Jinja2 templates
├── routes/          # Route definitions
├── blueprints/      # Application blueprints
└── app.py          # Main application file
```

## 🚦 Core Components

### 1. Blueprint System

Organize larger applications into modular components with blueprints:

```python
from typing import Dict, Any
from webpy import WebPy, Blueprint, Request, Response


# Create the main application
app = WebPy()

# Create a blueprint for user-related routes
ublueprint  = Blueprint('user', prefix='/user')


@ublueprint.route('/profile')
def profile(request: Request, response: Response) -> None:
    """
    User profile endpoint within the user blueprint.
    
    This route will be accessible at /user/profile due to the blueprint prefix.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Get user ID from request parameters or session
    id = request.queries.get('id', ['current'])[0]
    
    # In a real application, you would fetch user data from a database
    data = {
        'id': id,
        'username': 'example',
        'email': 'user@example.com'
    }
    
    response.json(data)


# Create a blueprint for admin-related routes
ablueprint = Blueprint('admin', prefix='/admin')


@ablueprint.route('/dashboard')
def dashboard(request: Request, response: Response) -> None:
    """
    Admin dashboard endpoint within the admin blueprint.
    
    This route will be accessible at /admin/dashboard due to the blueprint prefix.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # In a real application, you would fetch dashboard data from a database
    data = {
        'count': 1250,
        'sessions': 37,
        'status': {
            'cpu': '23%',
            'memory': '512MB / 4GB',
            'uptime': '7d 3h 45m'
        }
    }
    
    response.json(data)


# Register blueprints with the main application
app.blueprint(ublueprint)
app.blueprint(ablueprint)


if __name__ == '__main__':
    app.run(port=8080)
```

This blueprint feature lets you:

1. Group related routes together in separate files
2. Apply common configurations to groups of routes
3. Reuse components across different projects
4. Break large applications into logical, manageable units
5. Apply middleware selectively to specific blueprints

### 2. Creating Your First WebPy Application

```python
from typing import Optional
from webpy import WebPy


# Initialize the WebPy application instance
# This serves as the central object for the entire web application
app = WebPy()


def main() -> None:
    """
    Application entry point.
    
    Starts the WebPy server with the specified configuration.
    The server will listen on all network interfaces (0.0.0.0)
    on port 8080 by default.
    
    Returns:
        None: This function doesn't return any value
    """
    # Start the web server with the app instance
    # ip='0.0.0.0' binds to all available network interfaces
    # port=8080 specifies the port the server will listen on
    app.run(ip='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
```

### 3. Handling Requests

```python
from typing import Dict, Any, List, Optional
from webpy import WebPy, Request, Response


app = WebPy()


@app.route('/api/data', methods=['GET', 'POST'])
def handle_data(request: Request, response: Response) -> None:
    """
    Handle requests to the /api/data endpoint.
    
    Processes both GET and POST requests differently:
    - GET: Returns data based on page parameter and authentication
    - POST: Processes submitted JSON data
    
    Args:
        request: The incoming HTTP request object containing all request data
        response: The response object to be sent back to the client
        
    Returns:
        None: This function modifies the response object directly
    """
    if request.method == 'GET':
        # Extract the 'page' query parameter, defaulting to '1' if not provided
        page: str = request.queries.get('page', ['1'])[0]
        
        # Get the Authorization header value if present
        token: Optional[str] = request.headers.get('Authorization')
        
        # Log the request details for debugging purposes
        app.logger.debug(f"GET request received with page={page}, auth_token={auth_token}")
        
        # Prepare and send a JSON response
        response.json({
            'page': page,
            'data': 'example'
        })
    elif request.method == 'POST':
        # Parse the JSON data from the request body
        data: Dict[str, Any] = request.json()
        
        # Log the received data for debugging purposes
        app.logger.debug(f"POST request received with data: {data}")
        
        # Process the data (in a real application, you would do more here)
        # Send the processed data back as an API response
        response.api(data)
```

### 4. Dynamic Routing

```python
from typing import Dict, Any
from webpy import WebPy, Request, Response


app = WebPy()


@app.route('/users/<id:int>')
def get_user(request: Request, response: Response, id: int) -> None:
    """
    Retrieve user information based on user ID.
    
    This endpoint captures the dynamic 'id' parameter from the URL path.
    The :int type converter ensures the ID is treated as an integer.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        id: The user ID extracted from the URL path, converted to an integer
        
    Returns:
        None: This function modifies the response object directly
    """
    # In a real application, you would fetch user data from a database
    # For this example, we just return the captured ID
    app.logger.info(f"User information requested for ID: {id}")
    
    response.json({'id': id})


@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_resource(request: Request, response: Response) -> None:
    """
    RESTful endpoint to handle resources with multiple HTTP methods.
    
    This single endpoint handles all CRUD operations for the 'resources' collection:
    - GET: Retrieve resources
    - POST: Create a new resource
    - PUT: Update an existing resource
    - DELETE: Remove a resource
    
    Args:
        request: The incoming HTTP request object containing method and data
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Log the request method for audit purposes
    app.logger.info(f"Resource endpoint accessed with method: {request.method}")
    
    # Return the HTTP method used to access this endpoint
    # In a real application, you would implement the actual CRUD operations
    response.api({'method': request.method})
```

### 5. Using Templates

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
    <head>
        <title>{{ title }}</title>
        <!-- Template variables are injected using {{ variable_name }} syntax -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <!-- Dynamic content is inserted here -->
        <h1>Welcome, {{ name }}!</h1>
        
        <!-- You can also use conditionals and loops -->
        {% if messages %}
            <ul>
            {% for message in messages %}
                <li>{{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
    </body>
</html>
```

```python
from typing import Dict, Any, List
from webpy import WebPy, Request, Response


app = WebPy()


@app.route('/')
def index(request: Request, response: Response) -> None:
    """
    Render the index page using Jinja2 templates.
    
    This demonstrates how to use the templating system to generate
    dynamic HTML content based on variables passed to the template.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Sample data to demonstrate template variable injection
    context: Dict[str, Any] = {
        'title': 'Home',
        'name': 'Friend',
        'messages': ['Welcome to WebPy!', 'Enjoy your development journey!']
    }
    
    # Render the template with the provided context variables
    # The render method processes the template and substitutes variables
    html: str = app.render('index.html', **context)
    
    # Set the Content-Type header to indicate HTML content
    response.headers['Content-Type'] = 'text/html'
    
    # Encode the HTML string to bytes before sending
    response.body = html.encode('utf-8')
```

## 🧠 Advanced Features

### 1. Session Management

```python
from typing import Optional, Dict, Any
from webpy import WebPy, Request, Response, Sessions


app = WebPy()
sessions = Sessions()


@app.route('/login')
def login(request: Request, response: Response) -> None:
    """
    Handle user login and create a new session.
    
    This endpoint demonstrates how to create and manage user sessions.
    In a real application, you would verify credentials before creating a session.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Create a new session with a 1-hour expiration time
    # 'id' is the key in the session store
    # 'user123' is the value (typically a user identifier)
    # expires=3600 sets the session to expire after 3600 seconds (1 hour)
    sessions.add('id', 'user123', expires=3600)
    
    # Log the session creation for debugging purposes
    app.logger.info(f"New session created for user: user123")
    
    # Return a success message
    response.api({'message': 'Welcome aboard!'})


@app.route('/info')
def session_info(request: Request, response: Response) -> None:
    """
    Retrieve and display information about the current session.
    
    This endpoint checks if a valid session exists and returns its information.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Attempt to retrieve the session by its key
    # If no session exists, return 'No active session'
    id: str = sessions.get('id', 'No active session')
    
    # Log the session lookup
    app.logger.debug(f"Session lookup result: {session_id}")
    
    # Return the session information to the client
    response.json({'id': id})
```

### 2. Authentication

WebPy supports **Basic Authentication**, **JWT**, and **OAuth** out of the box.

```python
from typing import Dict, List, Any
from webpy import WebPy, Request, Response, Auth


app = WebPy()
auth = Auth(app)

# Set the JWT secret key used for signing tokens
auth.jwt.secret('secret')

# Configure role-based user identification
auth.roles({
    'admin': {
        'users': ['admin@example.com', 'superuser@example.com'],
        'permissions': ['read', 'write', 'delete', 'admin']
    },
    'user': {
        'users': ['user@example.com', 'customer@example.com'],
        'permissions': ['read', 'write']
    },
    'guest': {
        'permissions': ['read']
    }
})

# Configure OAuth providers for social authentication
auth.oauth.providers({
    'google': {
        'id': 'YOUR_GOOGLE_CLIENT_ID',
        'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
        'redirect': 'https://yourapp.com/oauth/google/callback',
        'scope': ['profile', 'email']
    }
})
```

#### Examples

##### 🔐 Basic Auth
```python
from typing import Dict, Any
from webpy import WebPy, Request, Response, Auth


app = WebPy()
auth = Auth(app)


@app.route('/basic-auth')
@auth.gates([auth.basic])  # Apply basic authentication protection
def basic_auth_route(request: Request, response: Response) -> None:
    """
    Basic authentication protected endpoint.
    
    This route requires valid HTTP Basic Authentication credentials
    before allowing access.
    
    Args:
        request: The incoming HTTP request object, including user info after auth
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # After successful authentication, user info is available in request.user
    username = request.user.get('username', 'anonymous')
    
    # Get the user's role based on their username/email
    user_role = auth.get_role(username)
    
    app.logger.info(f"Authenticated user accessed basic-auth endpoint: {username} (role: {user_role})")
    
    # Return a personalized greeting with role information
    response.json({
        "message": f"Hello, {username}!",
        "role": user_role,
        "permissions": auth.get_permissions(user_role)
    })
```

##### 🔑 JWT Auth
```python
from typing import Dict, Any
from webpy import WebPy, Request, Response, Auth


app = WebPy()
auth = Auth(app)


@app.route('/jwt-protected')
@auth.gates([auth.jwt])  # Apply JWT authentication protection
def jwt_protected_route(request: Request, response: Response) -> None:
    """
    JWT authentication protected endpoint.
    
    This route requires a valid JWT token in the Authorization header
    before allowing access.
    
    Args:
        request: The incoming HTTP request object with decoded user data
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    
    Notes:
        The JWT token should be sent in the Authorization header as:
        "Authorization: Bearer <token>"
    """
    # After successful JWT validation, request.user will contain the decoded payload
    username = request.user.get('username', 'anonymous')
    email = request.user.get('email', 'no-email')
    
    # Determine user role based on email
    user_role = auth.get_role(email)
    
    # Log the access for security monitoring
    app.logger.info(f"JWT authenticated user: {username} (role: {user_role})")
    
    # Return user information with role and permissions
    response.json({
        "message": f"Hello, {username}!",
        "email": email,
        "role": user_role,
        "can_admin": auth.has_permission(user_role, 'admin')
    })
```

##### 🌐 OAuth (Google)
```python
from typing import Dict, Any
from webpy import WebPy, Request, Response, Auth


app = WebPy()
auth = Auth(app)


@app.route('/oauth/google')
@auth.oauth(provider='google')
def oauth_google(request: Request, response: Response) -> None:
    """
    Initiate Google OAuth authentication flow.
    
    This endpoint redirects the user to Google's authentication page.
    No explicit implementation needed as the decorator handles the redirection.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: The decorator handles the OAuth initiation process
    """
    # The decorator handles the OAuth initiation process
    # This function body won't execute until after authentication
    pass


@app.route('/oauth/google/callback')
@auth.oauth.callback(provider='google')
def oauth_google_callback(request: Request, response: Response) -> None:
    """
    Handle the Google OAuth callback after successful authentication.
    
    This endpoint receives the OAuth code from Google, exchanges it for
    an access token, and retrieves user information.
    
    Args:
        request: The incoming HTTP request with the OAuth code and user data
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # After successful OAuth authentication, request.user will contain
    # the user profile information returned by Google
    name = request.user.get('name', 'User')
    email = request.user.get('email', 'No email provided')
    
    # Determine user role based on email address
    role = auth.role(email)
    
    # Log the successful OAuth login with role information
    app.logger.info(f"Google OAuth login: {name} ({email}) - Role: {role}")
    
    # Return a welcome message with the user's role information
    response.json({
        "message": f"Welcome, {name}!",
        "email": email,
        "role": role,
        "permissions": auth.get_permissions(roble)
    })
```

### 3. Role-Based Access Control (Access)

WebPy provides a simple yet powerful way to implement role-based access control.

```python
from typing import Dict, Any
from webpy import WebPy, Request, Response, Access


app = WebPy()
access = Access(app)


@app.route('/admin/dashboard')
@access.required(role='admin', permission='read')
def admin_dashboard(request: Request, response: Response) -> None:
    """
    Admin dashboard, restricted to admin users with 'read' permission.
    
    This route checks if the authenticated user has the admin role and
    read permission before allowing access.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    
    Notes:
        This endpoint requires authentication before the access check.
        Use it in combination with an authentication method.
    """
    # At this point, access control has verified the user has the required role and permission
    app.logger.info(f"Admin user accessed dashboard: {request.user.get('email')}")
    
    # Return admin dashboard data
    response.json({
        "message": "Welcome to the admin dashboard!",
        "stats": {
            "users": 1250,
            "active_sessions": 37,
            "server_load": "2.3"
        }
    })


@app.route('/user/profile')
@access.required(role='user', permission='read')
def user_profile(request: Request, response: Response) -> None:
    """
    User profile page, accessible to users with 'read' permission.
    
    This route checks if the authenticated user has at least the user role
    and read permission before allowing access.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    
    Notes:
        Since both 'admin' and 'user' roles have 'read' permission,
        both types of users can access this endpoint.
    """
    # At this point, access control has verified the user has the required role and permission
    app.logger.info(f"User viewed profile: {request.user.get('email')}")
    
    # Return user profile data
    response.json({
        "message": "Welcome to your profile!",
        "profile": {
            "name": request.user.get('name', 'User'),
            "email": request.user.get('email', 'No email provided'),
            "since": "2023-01-15"
        }
    })
```

### 4. CSRF Protection

WebPy includes built-in CSRF protection to secure your forms and APIs.

```python
from typing import Dict, Any
from webpy import WebPy, Request, Response, CSRF


app = WebPy()
csrf = CSRF(app)


@app.route('/submit', methods=['POST'])
@csrf.protect
def form_submission(request: Request, response: Response) -> None:
    """
    Handle form submissions with CSRF protection.
    
    This endpoint verifies the CSRF token before processing the form data.
    If the token is invalid or missing, the request will be rejected.
    
    Args:
        request: The incoming HTTP request with form data
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    
    Notes:
        The form must include a 'token' field that matches the token
        generated for the user's session.
    """
    # At this point, CSRF protection has verified the token is valid
    # Now we can safely process the form data
    data: Dict[str, Any] = request.form()
    
    # Log the form submission (excluding the CSRF token)
    data = {k: v for k, v in data.items() if k != 'token'}
    app.logger.info(f"Form submitted with data: {data}")
    
    # Process the form data (in a real application, you'd save to a database, etc.)
    
    # Return a success message
    response.json({
        "message": "Form submitted successfully!",
        "data": data
    })
```

To include a CSRF token in your forms:

```html
<form action="/submit" method="POST">
    <!-- The CSRF token is injected during template rendering -->
    <input type="hidden" name="token" value="{{ token }}">
    
    <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
    </div>
    
    <!-- Additional form fields -->
    
    <button type="submit">Submit</button>
</form>
```

### 5. Error Handling

Define custom error responses easily:

```python
from typing import Dict, Any
from webpy import WebPy, Request, Response


app = WebPy()


@app.error(404)
def not_found(request: Request, response: Response) -> None:
    """
    A handler for 404 Not Found errors.
    
    This function is called whenever a route is not found in the application.
    It allows for custom formatting of 404 error responses.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Log the not found error for monitoring
    app.logger.warning(f"404 Not Found: {request.path}")
    
    # Return a structured error response
    response.status = 404
    response.json({
        'error': 'Not Found',
        'path': request.path,
        'message': f"The requested resource '{request.path}' was not found on this server."
    })


@app.error(500)
def server_error(request: Request, response: Response) -> None:
    """
    A handler for 500 Internal Server Error.
    
    This function is called whenever an unhandled exception occurs in the application.
    It allows for custom formatting of 500 error responses.
    
    Args:
        request: The incoming HTTP request object
        response: The outgoing HTTP response object
        
    Returns:
        None: This function modifies the response object directly
    """
    # Log the server error for urgent review
    app.logger.error(f"500 Internal Server Error processing: {request.path}")
    
    # Return a structured error response
    # Note: In production, you should not expose detailed error information
    response.status = 500
    response.json({
        'error': 'Internal Server Error',
        'message': "The server encountered an unexpected condition that prevented it from fulfilling the request."
    })
```

### 6. HTTPS Support

Secure your application with HTTPS:

```python
from typing import Optional
from webpy import WebPy


app = WebPy()


def main() -> None:
    """
    Start the application with HTTPS support.
    
    This configures the application to use SSL/TLS encryption
    for secure HTTP communication.
    
    Returns:
        None: This function starts the web server and doesn't return
    """
    # Configure and start the HTTPS server
    app.run(
        ip='0.0.0.0',
        port=443,  # Standard HTTPS port
        certfile='path/to/cert.pem',  # SSL certificate file
        keyfile='path/to/key.pem'     # SSL private key file
    )
    
    # Log the server startup
    app.logger.info("HTTPS server started on port 443")


if __name__ == '__main__':
    main()
```

## 📜 License

WebPy is released under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
