# WebPy

WebPy is a lightweight and intuitive Python framework designed to simplify web development. Whether you're building a small web application or a complex API, WebPy provides the tools you need to get the job done efficiently and effectively.

## Core Features

WebPy comes packed with features to make web development straightforward and enjoyable:

- **Fast HTTP Handling**: Efficiently manage HTTP requests and responses.
- **Intelligent Routing**: Define routes with ease and flexibility.
- **Jinja2 Templates**: Create dynamic and reusable HTML templates.
- **Static File Serving**: Serve static files like CSS, JavaScript, and images effortlessly.
- **WebSocket Support**: Build real-time applications with WebSocket integration.
- **Session Management**: Handle user sessions securely and simply.
- **Middleware System**: Extend functionality with custom middleware.
- **HTTPS Support**: Secure your application with built-in HTTPS capabilities.
- **Custom Error Handling**: Define custom error pages and responses.

## Getting Started

To begin using WebPy, install it via pip:

```bash
pip install webpy
```

Here’s a suggested project structure to keep your application organized:

```
project/
├── static/          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/       # Jinja2 templates
├── middleware/      # Custom middleware
├── routes/          # Route definitions
└── app.py           # Main application file
```

## Core Components

### 1. Creating Your First WebPy Application

Starting a WebPy application is simple:

```python
from webpy import WebPy

app = WebPy()

if __name__ == '__main__':
    app.run(ip='0.0.0.0', port=8080)
```

### 2. Handling Requests

WebPy makes it easy to handle different types of HTTP requests:

```python
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data(request, response):
    if request.method == 'GET':
        page = request.queries.get('page', ['1'])[0]
        auth_token = request.headers.get('Authorization')
        
        response.json({
            'page': page,
            'data': 'example'
        })
    elif request.method == 'POST':
        data = request.json()
        response.api(data)
```

### 3. Dynamic Routing

Define dynamic routes to handle variable URL patterns:

```python
@app.route('/users/<id:int>')
def get_user(request, response, id):
    response.json({'user_id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_resource(request, response):
    response.api({'method': request.method})
```

### 4. Using Templates

WebPy integrates with Jinja2 for templating:

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
    <head><title>{{ title }}</title></head>
    <body>
        <h1>Welcome, {{ name }}!</h1>
    </body>
</html>
```

```python
@app.route('/')
def index(request, response):
    html = app.render('index.html', title='Home', name='Friend')
    response.headers['Content-Type'] = 'text/html'
    response.body = html.encode('utf-8')
```

## Advanced Features

### 1. Session Management

Manage user sessions with ease:

```python
from webpy import Sessions

sessions = Sessions()

@app.route('/login')
def login(request, response):
    sessions.add('session_id', 'user123', expires=3600)
    response.api({'message': 'Welcome aboard!'})

@app.route('/session-info')
def session_info(request, response):
    session_id = sessions.get('session_id', 'No active session')
    response.json({'session_id': session_id})
```

### 2. Middleware

Extend your application with custom middleware:

```python
from webpy import Middleware

middleware = Middleware(app)

@middleware.register
def logging_middleware(request, response):
    print(f"Incoming: {request.method} {request.path}")

@middleware.register
def cors_middleware(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'

@app.route('/api/protected')
@middleware.run()
def protected_route(request, response):
    response.api({'data': 'protected'})
```

### 3. WebSocket Support

Build real-time features with WebSocket:

```python
from webpy import Socket

socket = Socket(app)

@socket.on('connect')
def handle_connect(data, conn):
    print(f"New connection: {conn}")

@socket.on('message')
def handle_message(data, conn):
    socket.emit('broadcast', {'message': data['message']})

if __name__ == '__main__':
    app.run(port=8080)
    socket.run(port=8081)
```

### 4. Custom Error Handling

Define custom error responses:

```python
@app.error(404)
def not_found(request, response):
    response.json({
        'error': 'Not Found',
        'path': request.path
    })

@app.error(500)
def server_error(request, response):
    response.json({
        'error': 'Internal Server Error'
    })
```

### 5. HTTPS Support

Secure your application with HTTPS:

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

WebPy is released under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.