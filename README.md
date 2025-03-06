# WebPy

WebPy is a lightweight Python framework designed to simplify web development. Whether you're building a small web app or a complex API, WebPy provides the tools you need to get the job done efficiently.


## 🚀 Core Features

| Feature                | Description                                             |
|------------------------|---------------------------------------------------------|
| Fast HTTP Handling     | Efficiently manage HTTP requests and responses.         |
| Smart Routing          | Define routes with ease and flexibility.               |
| Jinja2 Templates       | Create dynamic and reusable HTML templates.            |
| Static File Serving    | Serve static files like CSS, JavaScript, and images.   |
| WebSocket Support      | Build real-time applications with WebSocket.           |
| Session Management     | Handle user sessions securely and simply.              |
| HTTPS Support          | Secure your app with built-in HTTPS.                   |
| Error Handling         | Define custom error pages and responses.               |
| Auth Support           | Basic, JWT, and OAuth integrations.                    |
| Role-Based Access      | Control access to routes based on user roles.          |
| CSRF Protection        | Protect your app from CSRF attacks.                    |
| Blueprint System       | Organize your app into modular components.             |

---

## 🏗️ Project Structure

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

---

## 🚦 Core Components

### 1. Blueprint System

Organize larger apps into modular components with blueprints:

```python
from webpy import WebPy, Blueprint, Request, Response

# Initialize the app
app = WebPy()

# User blueprint
user = Blueprint('user', prefix='/user')

@user.route('/profile')
def profile(request: Request, response: Response) -> None:
    """
    Handle user profile requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    id = request.queries.get('id', ['current'])[0]
    response.json({'id': id, 'name': 'John'})

# Admin blueprint
admin = Blueprint('admin', prefix='/admin')

@admin.route('/dashboard')
def dashboard(request: Request, response: Response) -> None:
    """
    Handle admin dashboard requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    response.json({'stats': {'users': 1250, 'sessions': 37}})

# Register blueprints
app.blueprint(user)
app.blueprint(admin)

if __name__ == '__main__':
    app.run(port=8080)
```

---

### 2. Creating Your First App

```python
from webpy import WebPy

# Initialize the app
app = WebPy()

def main() -> None:
    """
    Entry point for the application.
    Starts the WebPy server on port 8080.
    """
    app.run(ip='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
```

---

### 3. Handling Requests

```python
from webpy import WebPy, Request, Response

# Initialize the app
app = WebPy()

@app.route('/api/data', methods=['GET', 'POST'])
def data(request: Request, response: Response) -> None:
    """
    Handle API data requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    if request.method == 'GET':
        page = request.queries.get('page', ['1'])[0]
        response.json({'page': page, 'data': 'example'})
    elif request.method == 'POST':
        data = request.json()
        response.api(data)
```

---

### 4. Dynamic Routing

```python
from webpy import WebPy, Request, Response

# Initialize the app
app = WebPy()

@app.route('/users/<id:int>')
def user(request: Request, response: Response, id: int) -> None:
    """
    Handle user-specific requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
        id: The user ID extracted from the URL.
    """
    response.json({'id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def resource(request: Request, response: Response) -> None:
    """
    Handle resource requests for CRUD operations.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    response.api({'method': request.method})
```

---

### 5. Using Templates

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

# Initialize the app
app = WebPy()

@app.route('/')
def index(request: Request, response: Response) -> None:
    """
    Render the index page using Jinja2 templates.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    context = {
        'title': 'Home',
        'name': 'Friend',
        'messages': ['Welcome to WebPy!', 'Enjoy your development journey!']
    }
    html = app.render('index.html', **context)
    response.headers['Content-Type'] = 'text/html'
    response.body = html.encode('utf-8')
```

---

## 🧠 Advanced Features

### 1. Session Management

```python
from webpy import WebPy, Request, Response, Sessions

# Initialize the app and sessions
app = WebPy()
sessions = Sessions()

@app.route('/login')
def login(request: Request, response: Response) -> None:
    """
    Handle user login and create a session.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    sessions.add('id', 'user123', expires=3600)
    response.api({'message': 'Welcome aboard!'})

@app.route('/info')
def info(request: Request, response: Response) -> None:
    """
    Retrieve session information.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    id = sessions.get('id', 'No active session')
    response.json({'id': id})
```

### 2. Authentication

WebPy supports **Basic Authentication**, **JWT**, and **OAuth** out of the box.

```python
from webpy import WebPy, Request, Response, Auth

# Initialize the app and auth
app = WebPy()
auth = Auth(app)

# Set JWT secret key
auth.jwt.secret('secret')

# Configure roles
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

# Configure OAuth providers
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
@app.route('/basic-auth')
def basic(request: Request, response: Response) -> None:
    """
    Handle basic authentication-protected requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    username = request.user.get('username', 'anonymous')
    response.json({
        "message": f"Hello, {username}!",
        "role": auth.roles.get_role(username)
    })
```

##### 🔑 JWT Auth
```python
@app.route('/jwt-protected')
def jwt(request: Request, response: Response) -> None:
    """
    Handle JWT authentication-protected requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    username = request.user.get('username', 'anonymous')
    response.json({
        "message": f"Hello, {username}!",
        "role": auth.roles.get_role(username)
    })
```

##### 🌐 OAuth (Google)
```python
@app.route('/oauth/google')
@auth.oauth(provider='google')
def google(request: Request, response: Response) -> None:
    """
    Initiate Google OAuth authentication.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    pass

@app.route('/oauth/google/callback')
@auth.oauth.callback(provider='google')
def google_callback(request: Request, response: Response) -> None:
    """
    Handle Google OAuth callback.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    name = request.user.get('name', 'User')
    response.json({
        "message": f"Welcome, {name}!",
        "role": auth.roles.get_role(request.user.get('email'))
    })
```

### 3. Role-Based Access Control

```python
from webpy import WebPy, Request, Response, Auth

# Initialize the app and auth
app = WebPy()
auth = Auth(app)

@app.route('/admin/dashboard')
@auth.required(role='admin', permission='read')
def dashboard(request: Request, response: Response) -> None:
    """
    Handle admin dashboard requests.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    response.json({
        "message": "Welcome to the admin dashboard!",
        "stats": {'users': 1250, 'sessions': 37}
    })
```

---

### 4. CSRF Protection

```python
from webpy import WebPy, Request, Response, CSRF

# Initialize the app and CSRF
app = WebPy()
csrf = CSRF(app)

@app.route('/submit', methods=['POST'])
@csrf.protect
def submit(request: Request, response: Response) -> None:
    """
    Handle form submissions with CSRF protection.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    data = request.form()
    response.json({
        "message": "Form submitted successfully!",
        "data": data
    })
```

---

### 5. Error Handling

```python
from webpy import WebPy, Request, Response

# Initialize the app
app = WebPy()

@app.error(404)
def not_found(request: Request, response: Response) -> None:
    """
    Handle 404 Not Found errors.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    response.status = 404
    response.json({
        'error': 'Not Found',
        'path': request.path
    })

@app.error(500)
def server_error(request: Request, response: Response) -> None:
    """
    Handle 500 Internal Server Errors.
    
    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
    """
    response.status = 500
    response.json({
        'error': 'Internal Server Error'
    })
```

### 6. HTTPS Support

```python
from webpy import WebPy

# Initialize the app
app = WebPy()

def main() -> None:
    """
    Start the app with HTTPS support.
    """
    app.run(
        ip='0.0.0.0',
        port=443,
        certfile='path/to/cert.pem',
        keyfile='path/to/key.pem'
    )

if __name__ == '__main__':
    main()
```
