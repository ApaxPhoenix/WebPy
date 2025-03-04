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
| Middleware System      | Extend functionality with custom middleware.           |
| HTTPS Support          | Secure your application with built-in HTTPS.           |
| Custom Error Handling  | Define custom error pages and responses.               |
| Authentication Support | Basic, JWT, and OAuth integrations.                    |
| Role-Based Access      | Control access to routes based on user roles.          |
| CSRF Protection        | Protect your application from Cross-Site Request Forgery attacks. |

## 🏗️ Project Structure

To keep your application organized, we suggest the following structure:

```
project/
├── static/          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/       # Jinja2 templates
├── middleware/      # Custom middleware
├── routes/          # Route definitions
└── app.py          # Main application file
```

## 🚦 Core Components

### 1. Creating Your First WebPy Application

```python
from webpy import WebPy

app = WebPy()

if __name__ == '__main__':
    app.run(ip='0.0.0.0', port=8080)
```

### 2. Handling Requests

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

```python
@app.route('/users/<id:int>')
def get_user(request, response, id):
    response.json({'user_id': id})

@app.route('/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_resource(request, response):
    response.api({'method': request.method})
```

### 4. Using Templates

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

## 🧠 Advanced Features

### 1. Session Management

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

### 3. Authentication

WebPy supports **Basic Authentication**, **JWT**, and **OAuth** out of the box.

```python
from webpy import WebPy, Auth

app = WebPy()
auth = Auth(app)

auth.jwt.secret('your_super_secret_key')

auth.basic.users([
    {"username": "admin", "password": "password123"},
    {"username": "user", "password": "pass456"}
])

auth.oauth.providers({
    'google': {
        'client_id': 'YOUR_GOOGLE_CLIENT_ID',
        'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
        'redirect_uri': 'https://yourapp.com/oauth/google/callback',
        'scope': ['profile', 'email']
    }
})
```

#### Examples

##### 🔐 Basic Auth
```python
@app.route('/basic-auth')
@auth.gates([auth.basic])
def basic_auth_route(request, response):
    response.json({"message": f"Hello, {request.user}!"})
```

##### 🔑 JWT Auth
```python
@app.route('/jwt-protected')
@auth.gates([auth.jwt])
def jwt_protected_route(request, response):
    response.json({"message": f"Hello, {request.user['username']}!"})
```

##### 🌐 OAuth (Google)
```python
@app.route('/oauth/google')
@auth.oauth(provider='google')
def oauth_google(request, response):
    pass
```

```python
@app.route('/oauth/google/callback')
@auth.oauth.callback(provider='google')
def oauth_google_callback(request, response):
    response.json({"message": f"Welcome, {request.user['name']}!"})
```

### 4. Role-Based Access Control (Access)

WebPy provides a simple yet powerful way to implement role-based access control.

```python
from webpy import Access

access = Access(app)

# Define roles and permissions
access.roles({
    'admin': ['create', 'read', 'update', 'delete'],
    'user': ['read']
})

@app.route('/admin/dashboard')
@access.required(role='admin', permission='read')
def admin_dashboard(request, response):
    response.json({"message": "Welcome to the admin dashboard!"})

@app.route('/user/profile')
@access.required(role='user', permission='read')
def user_profile(request, response):
    response.json({"message": "Welcome to your profile!"})
```

### 5. CSRF Protection

WebPy includes built-in CSRF protection to secure your forms and APIs.

```python
from webpy import CSRF

csrf = CSRF(app)

@app.route('/submit-form', methods=['POST'])
@csrf.protect
def submit_form(request, response):
    data = request.form()
    response.json({"message": "Form submitted successfully!"})
```

To include a CSRF token in your forms:

```html
<form action="/submit-form" method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

### 6. WebSocket Support

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

### 7. Custom Error Handling

Define custom error responses easily:

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

### 8. HTTPS Support

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

## 📜 License

WebPy is released under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
