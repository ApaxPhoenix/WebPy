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
| **Auth Support**        | Basic, JWT, and OAuth integrations.                         |
| **Role-Based Access**   | Control access to routes based on user roles.               |
| **CSRF Protection**     | Protect your app from CSRF attacks.                         |
| **Blueprint System**    | Organize your app into modular components.                  |

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
└── app.py          # Main app file
```

## Core Components

### Creating Your First App

To create a simple WebPy app, initialize the `WebPy` class and define your routes. The `app.run()` method starts the server.

```python
from webpy import WebPy

app = WebPy()

def main():
    app.run(ip='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
```

### Handling Requests

WebPy makes it easy to handle different HTTP methods (GET, POST, etc.) and extract data from requests.

```python
from webpy import WebPy, Request, Response

app = WebPy()

@app.route('/api/data', methods=['GET', 'POST'])
def data(request, response):
    if request.method == 'GET':
        page = request.queries.get('page', ['1'])[0]
        response.json({'page': page, 'data': 'example'})
    elif request.method == 'POST':
        data = request.json()
        response.api(data)
```

### Dynamic Routing

WebPy supports dynamic routing, allowing you to extract variables from the URL.

```python
from webpy import WebPy, Request, Response

app = WebPy()

@app.route('/users/<id:int>')
def user(request, response, id):
    response.json({'id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def resource(request, response):
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

app = WebPy()

@app.route('/')
def index(request, response):
    context = {
        'title': 'Home',
        'name': 'Friend',
        'messages': ['Welcome to WebPy!', 'Enjoy your development journey!']
    }
    html = app.render('index.html', **context)
    response.headers['Content-Type'] = 'text/html'
    response.body = html.encode('utf-8')
```

### Blueprint System

Organize larger apps into modular components with blueprints. Blueprints allow you to group related routes and functionality together, making your codebase more maintainable.

```python
from webpy import WebPy, Blueprint, Request, Response

app = WebPy()

user = Blueprint('user', prefix='/user')

@user.route('/profile')
def profile(request, response):
    id = request.queries.get('id', ['current'])[0]
    response.json({'id': id, 'name': 'John'})

admin = Blueprint('admin', prefix='/admin')

@admin.route('/dashboard')
def dashboard(request, response):
    response.json({'stats': {'users': 1250, 'sessions': 37}})

app.blueprint(user)
app.blueprint(admin)

if __name__ == '__main__':
    app.run(port=8080)
```

### Session Management

WebPy provides built-in session management to handle user sessions securely.

```python
from webpy import WebPy, Request, Response, Sessions

app = WebPy()
sessions = Sessions()

@app.route('/login')
def login(request, response):
    sessions.add('id', 'user123', expires=3600)
    response.api({'message': 'Welcome aboard!'})

@app.route('/info')
def info(request, response):
    id = sessions.get('id', 'No active session')
    response.json({'id': id})
```

### Authentication

WebPy supports **Basic Authentication** and **OAuth** out of the box.

```python
from webpy import WebPy, Request, Response, Auth

app = WebPy()
auth = Auth(app)

auth.roles({
    'admin': {
        'users': ['admin@example.com'],
        'permissions': ['read', 'write', 'delete']
    },
    'user': {
        'users': ['user@example.com'],
        'permissions': ['read', 'write']
    }
})

auth.oauth.providers({
    'example': {
        'id': '<CLIENT_ID>',
        'secret': '<CLIENT_SECRET>',
        'redirect': 'https://example.com/oauth/callback',
        'scope': ['profile', 'email']
    }
})
```

#### Basic Auth

```python
@app.route('/basic-auth')
def basic(request, response):
    username = request.user.get('username', 'anonymous')
    response.json({
        "message": f"Hello, {username}!",
        "role": auth.roles.get(username)
    })
```

#### OAuth

```python
@app.route('/oauth/example')
@auth.oauth(provider='example')
def google(request, response):
    pass

@app.route('/oauth/example/callback')
@auth.oauth.callback(provider='example')
def google_callback(request, response):
    name = request.user.get('name', 'User')
    response.json({
        "message": f"Welcome, {name}!",
        "role": auth.roles.get(request.user.get('email'))
    })
```

### Role-Based Access Control

WebPy allows you to control access to routes based on user roles.

```python
from webpy import WebPy, Request, Response, Auth

app = WebPy()
auth = Auth(app)

@app.route('/admin/dashboard')
@auth.required(role='admin', permission='read')
def dashboard(request, response):
    response.json({
        "message": "Welcome to the admin dashboard!",
        "stats": {'users': 1250, 'sessions': 37}
    })
```

### CSRF Protection

WebPy provides built-in CSRF protection to secure your forms.

```python
from webpy import WebPy, Request, Response, CSRF

app = WebPy()
csrf = CSRF(app)

@app.route('/submit', methods=['POST'])
@csrf.protect
def submit(request, response):
    data = request.form()
    response.json({
        "message": "Form submitted successfully!",
        "data": data
    })
```

### Error Handling

WebPy allows you to define custom error pages and responses.

```python
from webpy import WebPy, Request, Response

app = WebPy()

@app.error(404)
def not_found(request, response):
    response.status = 404
    response.json({
        'error': 'Not Found',
        'path': request.path
    })

@app.error(500)
def server_error(request, response):
    response.status = 500
    response.json({
        'error': 'Internal Server Error'
    })
```

### HTTPS Support

WebPy supports HTTPS out of the box, allowing you to secure your app with SSL/TLS.

```python
from webpy import WebPy

app = WebPy()

def main():
    app.run(
        ip='0.0.0.0',
        port=443,
        certfile='path/to/cert.pem',
        keyfile='path/to/key.pem'
    )

if __name__ == '__main__':
    main()
```

This documentation provides a comprehensive guide to using WebPy for your web development needs. By following the examples and explanations provided, you can quickly get started with building robust and scalable web applications using WebPy.
