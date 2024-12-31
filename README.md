# WebPy: Modern Python Web Framework

A minimalist Python framework for building lightweight and efficient web applications effortlessly.

## Core Features
- HTTP request/response handling
- Dynamic routing with path parameters
- Template rendering (Jinja2)
- Static file serving
- WebSocket support
- Session management
- Middleware pipeline
- HTTPS support
- Custom error handling

## Installation & Basic Setup

```bash
pip install webpy
```

Basic project structure:
```
project/
├── static/          # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/       # Jinja2 templates
├── middleware/      # Custom middleware
├── routes/          # Route handlers
└── app.py          # Main application
```

## Core Components

### 1. Application Setup

```python
from webpy import WebPy

app = WebPy()

if __name__ == '__main__':
    app.run(ip='0.0.0.0', port=8080)
```

### 2. Request Handling

```python
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data(request, response):
    """
    Handles GET and POST requests to the `/api/data` endpoint.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    if request.method == 'GET':
        # Access query parameters
        page = request.queries.get('page', ['1'])[0]
        
        # Access headers
        auth_token = request.headers.get('Authorization')
        
        response.json({
            'page': page,
            'data': 'example'
        })
    elif request.method == 'POST':
        # Parse JSON body
        data = request.json()
        response.api(data)  # Returns 201 for POST
```

### 3. Dynamic Routing

```python
@app.route('/users/<id:int>')
def get_user(request, response, id):
    """
    Retrieve a user by their ID.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
        id: The user ID extracted from the URL path.
    """
    response.json({'user_id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_resource(request, response):
    """
    Handle CRUD operations for resources.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    response.api({'method': request.method})
```

### 4. Template Rendering

```python
# templates/index.html
"""
<!DOCTYPE html>
<html>
    <head><title>{{ title }}</title></head>
    <body>
        <h1>Welcome, {{ name }}!</h1>
    </body>
</html>
"""

@app.route('/')
def index(request, response):
    """
    Render the homepage.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    html = app.render('index.html',
        title='Home',
        name='User'
    )
    response.headers['Content-Type'] = 'text/html'
    response.body = html.encode('utf-8')
```

## Advanced Features

### 1. Session Management

```python
from webpy import Sessions

sessions = Sessions()

@app.route('/login')
def login(request, response):
    """
    Log in a user and start a session.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    # Set session with 1 hour expiry
    sessions.add('session_id', 'user123', expires=3600)
    response.api({'message': 'Logged in'})

@app.route('/session-info')
def session_info(request, response):
    """
    Retrieve session information.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    session_id = sessions.get('session_id', 'No active session')
    response.json({'session_id': session_id})
```

### 2. Middleware Pipeline

```python
from webpy import Middleware

middleware = Middleware(app)

@middleware.register
def logging_middleware(request, response):
    """
    Logs details of incoming requests.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object.
    """
    print(f"Request: {request.method} {request.path}")

@middleware.register
def cors_middleware(request, response):
    """
    Adds CORS headers to responses.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.route('/api/protected')
@middleware.run()
def protected_route(request, response):
    """
    A protected route that applies middleware.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object.
    """
    response.api({'data': 'protected'})
```

### 3. WebSocket Integration

```python
from webpy import Socket

socket = Socket(app)

@socket.on('connect')
def handle_connect(data, conn):
    """
    Handle WebSocket connection.

    Args:
        data: Data sent by the client.
        conn: The WebSocket connection object.
    """
    print(f"Client connected: {conn}")

@socket.on('message')
def handle_message(data, conn):
    """
    Handle incoming WebSocket messages.

    Args:
        data: Data sent by the client.
        conn: The WebSocket connection object.
    """
    socket.emit('broadcast', {
        'message': data['message']
    })

if __name__ == '__main__':
    app.run(port=8080)  # HTTP server
    socket.run(port=8081)  # WebSocket server
```

### 4. Error Handling

```python
@app.error(404)
def not_found(request, response):
    """
    Handle 404 Not Found errors.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    response.json({
        'error': 'Not Found',
        'path': request.path
    })

@app.error(500)
def server_error(request, response):
    """
    Handle 500 Internal Server Errors.

    Args:
        request: The incoming HTTP request object.
        response: The HTTP response object to populate.
    """
    response.json({
        'error': 'Internal Server Error'
    })
```

### 5. HTTPS Configuration

```python
if __name__ == '__main__':
    app.run(
        ip='0.0.0.0',
        port=443,
        certfile='path/to/cert.pem',
        keyfile='path/to/key.pem'
    )
```

## License

WebPy is published under the MIT License. See [LICENSE](LICENSE) for details.
