# WebPy Documentation

**WebPy** is a lightweight Python framework designed to simplify web development. Whether you're building a small web application or a complex API, WebPy provides the tools you need to get the job done efficiently. This documentation will guide you through the core features, project structure, and essential functionalities of WebPy.

## Core Features

| **Feature**            | **Description**                                             |
|-------------------------|-------------------------------------------------------------|
| **Fast HTTP Handling**  | Efficiently manage HTTP requests and responses.             |
| **Smart Routing**       | Define routes with ease and flexibility.                    |
| **Jinja2 Templates**    | Create dynamic and reusable HTML templates.                 |
| **Static File Serving** | Serve static files like CSS, JavaScript, and images.        |
| **WebSocket Support**   | Build real-time applications with WebSocket.                |
| **Session Management**  | Handle user sessions securely and simply.                   |
| **HTTPS Support**       | Secure your app with built-in HTTPS.                        |
| **Error Handling**      | Define custom error pages and responses.                    |
| **CSRF Protection**     | Protect your app from CSRF attacks.                         |
| **Blueprint System**    | Organize your app into modular components.                  |
| **Middleware System**   | Process requests/responses through customizable pipelines.  |

## Project Structure

A typical WebPy project is organized as follows:

```
project/
├── static/          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/       # Jinja2 templates
├── routes/          # Route definitions
├── blueprints/      # App blueprints
├── middleware/      # Custom middleware components
└── app.py          # Main app file
```

## Core Components

### Creating Your First App

To create a simple WebPy app, initialize the `WebPy` class and define your routes. The `app.run()` method starts the server.

```python
from webpy import WebPy
from typing import Dict, Any, Optional

# Initialize the WebPy application
app = WebPy()

def main() -> None:
    """
    Main entry point for the application.
    Starts the WebPy server with the specified configuration.
    """
    # Start the server on all network interfaces (0.0.0.0) on port 8080
    app.run(ip='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
```

### Handling Requests

WebPy makes it easy to handle different HTTP methods (GET, POST, etc.) and extract data from requests.

```python
from webpy import WebPy, Request, Response
from typing import Dict, Any, Optional, List, Union

# Initialize the WebPy application
app = WebPy()

@app.route('/api/data', methods=['GET', 'POST'])
def data(request: Request, response: Response) -> None:
    """
    Handle API requests for the /api/data endpoint.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    if request.method == 'GET':
        # Extract the 'page' query parameter, defaulting to '1' if not provided
        page = request.queries.get('page', ['1'])[0]
        
        # Return JSON data with the page number and example data
        response.json({'page': page, 'data': 'example'})
    elif request.method == 'POST':
        # Parse JSON data from the request body
        data: Dict[str, Any] = request.json()
        
        # Return the received data as an API response
        response.api(data)
```

### Dynamic Routing

WebPy supports dynamic routing, allowing you to extract variables from the URL.

```python
from webpy import WebPy, Request, Response
from typing import Dict, Any, Optional, List, Union

# Initialize the WebPy application
app = WebPy()

@app.route('/users/<id:int>')
def user(request: Request, response: Response, id: int) -> None:
    """
    Handle requests for individual user information.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        id: User ID extracted from the URL path
        
    Returns:
        None: The function modifies the response object directly
    """
    # Return JSON data with the user ID
    response.json({'id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def resource(request: Request, response: Response) -> None:
    """
    RESTful endpoint handling multiple HTTP methods for resource management.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Return the HTTP method used in the request
    response.api({'method': request.method})
```

### Using Templates

WebPy integrates with **Jinja2** for templating, allowing you to create dynamic HTML pages.

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
    <head>
        <title>{{ title }}</title>
    </head>
    <body>
        <h1>Welcome, {{ name }}!</h1>
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
from webpy import WebPy, Request, Response
from typing import Dict, List, Any, Optional

# Initialize the WebPy application
app = WebPy()

@app.route('/')
def index(request: Request, response: Response) -> None:
    """
    Render the index page with dynamic content.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Prepare context data to be passed to the template
    context: Dict[str, Any] = {
        'title': 'Home',
        'name': 'Friend',
        'messages': ['Welcome to WebPy!', 'Enjoy your development journey!']
    }
    
    # Render the template with the context data
    html: str = app.render('index.html', **context)
    
    # Set the Content-Type header and response body
    response.headers['Content-Type'] = 'text/html'
    response.body = html.encode('utf-8')
```

### Blueprint System

Organize larger apps into modular components with blueprints. Blueprints allow you to group related routes and functionality together, making your codebase more maintainable.

```python
from webpy import WebPy, Blueprint, Request, Response
from typing import Dict, Any, Optional

# Initialize the WebPy application
app = WebPy()

# Create a blueprint for user-related routes
user = Blueprint('user', prefix='/user')

@user.route('/profile')
def profile(request: Request, response: Response) -> None:
    """
    Handle requests for user profile information.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Extract the user ID from query parameters, defaulting to 'current'
    id: str = request.queries.get('id', ['current'])[0]
    
    # Return JSON data with user information
    response.json({'id': id, 'name': 'John'})

# Create a blueprint for admin-related routes
admin = Blueprint('admin', prefix='/admin')

@admin.route('/dashboard')
def dashboard(request: Request, response: Response) -> None:
    """
    Handle requests for the admin dashboard.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Return JSON data with dashboard statistics
    response.json({'stats': {'users': 1250, 'sessions': 37}})

# Register blueprints with the application
app.blueprint(user)
app.blueprint(admin)

if __name__ == '__main__':
    # Start the server on port 8080
    app.run(port=8080)
```

### Session Management

WebPy provides built-in session management to handle user sessions securely.

```python
from webpy import WebPy, Request, Response, Sessions, Middleware
from typing import Dict, Any, Optional, Union

# Initialize the WebPy application
app = WebPy()

# Initialize the Sessions module
sessions = Sessions()

@app.route('/login')
def login(request: Request, response: Response) -> None:
    """
    Handle user login and session creation.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Add a session variable 'id' with value 'user123' that expires in 3600 seconds (1 hour)
    sessions.add('id', 'user123', expires=3600)
    
    # Return a success message
    response.api({'message': 'Welcome aboard!'})

@app.route('/info')
def info(request: Request, response: Response) -> None:
    """
    Retrieve and display session information.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Get the session ID, defaulting to 'No active session' if not found
    id: str = sessions.get('id', 'No active session')
    
    # Return the session ID as JSON
    response.json({'id': id})
```

### Middleware System

WebPy includes a Middleware system for processing requests and responses. Below is a simple example showing how to use the Middleware class to track user activity.

#### Using Middleware for User Tracking

```python
from webpy import WebPy, Middleware, Request, Response
from typing import Dict, Any

# Initialize the WebPy application
app = WebPy()

# Initialize the middleware
middleware = Middleware(app)

# Create a user tracking middleware function
@middleware.register
def joins(request: Request, response: Response) -> None:
    """
    Track when users join the application.
    
    Args:
        request: The Request object
        response: The Response object
    """
    # Check if this is a new session
    if not request.session.get('visited'):
        print(f"User has joined: {request.remote.address}")
        request.session['visited'] = True
    
    # Log the page visit
    print(f"User accessed: {request.path}")

# Create a middleware to detect when users leave
@middleware.register
def leaves(request: Request, response: Response) -> None:
    """
    Track when users might be leaving the application.
    
    Args:
        request: The Request object
        response: The Response object
    """
    # Check if this is a typical exit pattern (like navigating to logout)
    if request.path == '/logout' or request.path == '/exit':
        print(f"User has left: {request.remote.address}")
        # Clear session data
        request.session.clear()

# Apply middleware to all routes by default
@app.route('/')
def homepage(request: Request, response: Response) -> None:
    """
    Homepage with user tracking middleware.
    """
    response.json({
        'message': 'Welcome to the homepage!'
    })

# Apply only user tracking to the about page
@app.route('/about')
def about(request: Request, response: Response) -> None:
    """
    About page with only user tracking middleware.
    """
    response.json({
        'about': 'WebPy Framework',
        'version': '1.0.0'
    })

# Example of excluding middleware from a specific route
@app.route('/api/health')
@middleware.exclude
def health_check(request: Request, response: Response) -> None:
    """
    Health check endpoint without any middleware.
    """
    response.json({
        'status': 'healthy'
    })
```

### CSRF Protection

WebPy provides built-in CSRF protection to secure your forms.

```python
from webpy import WebPy, Request, Response, CSRF
from typing import Dict, Any, Optional

# Initialize the WebPy application
app = WebPy()

# Initialize the CSRF protection module
csrf = CSRF(app)

@app.route('/submit', methods=['POST'])
@csrf.protect
def submit(request: Request, response: Response) -> None:
    """
    Handle form submissions with CSRF protection.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
        
    Notes:
        This route is protected by CSRF token validation through the csrf.protect decorator.
        The form must include a valid CSRF token for the request to be processed.
    """
    # Parse form data from the request
    data: Dict[str, Any] = request.form()
    
    # Return a success message and the submitted data
    response.json({
        "message": "Form submitted successfully!",
        "data": data
    })
```

### Error Handling

WebPy allows you to define custom error pages and responses.

```python
from webpy import WebPy, Request, Response
from typing import Dict, Any, Optional

# Initialize the WebPy application
app = WebPy()

@app.error(404)
def not_found(request: Request, response: Response) -> None:
    """
    Custom handler for 404 Not Found errors.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Set the HTTP status code to 404
    response.status = 404
    
    # Return JSON with error information including the requested path
    response.json({
        'error': 'Not Found',
        'path': request.path
    })

@app.error(500)
def server_error(request: Request, response: Response) -> None:
    """
    Custom handler for 500 Internal Server Error.
    
    Args:
        request: The Request object containing all request information
        response: The Response object to be populated with the response data
        
    Returns:
        None: The function modifies the response object directly
    """
    # Set the HTTP status code to 500
    response.status = 500
    
    # Return JSON with error information
    response.json({
        'error': 'Internal Server Error'
    })
```

### HTTPS Support

WebPy supports HTTPS out of the box, allowing you to secure your app with SSL/TLS.

```python
from webpy import WebPy
from typing import Optional

# Initialize the WebPy application
app = WebPy()

def main() -> None:
    """
    Main entry point for the application.
    Starts the WebPy server with HTTPS enabled.
    
    Notes:
        The certfile and keyfile parameters specify the paths to the SSL/TLS certificate
        and private key files required for HTTPS.
    """
    # Start the server on all network interfaces (0.0.0.0) on port 443 (default HTTPS port)
    # with SSL/TLS enabled using the specified certificate and key files
    app.run(
        ip='0.0.0.0',
        port=443,
        certfile='path/to/cert.pem',  # Path to SSL/TLS certificate
        keyfile='path/to/key.pem'     # Path to private key
    )

if __name__ == '__main__':
    main()
```
