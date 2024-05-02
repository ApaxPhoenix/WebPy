# WebPy

WebPy is a compact Python micro-framework, simplifying web development with its minimalist approach. Build lightweight and efficient web applications effortlessly.

## Introduction

MicroWeb is designed to make web development quick and easy, with the flexibility to scale up to more complex projects. It provides a lightweight framework for building web applications in Python.

## Features

- Lightweight and minimalist
- Simplified project structure
- No enforced dependencies
- Easy to scale and extend with community-provided extensions

## Getting Started

To get started with MicroWeb, follow these simple steps:

1. Install WebPy using pip:

```
pip install webpy
```

2. Create a new Python file for your web application, e.g., `app.py`.

3. Write your web application code using WebPy's simple routing system.

```python
from webpy import WebPy

# Instantiate the WebPyApp wrapper
web_app = WebPy()

# Define a route and corresponding handler function
@web_app.route("/hello", methods=['GET'])
def hello(request, response):
    if request.method == 'GET':
        # Return a simple HTML page
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hello Page</title>
        </head>
        <body>
            <h1>Hello, World!</h1>
        </body>
        </html>
        """
        # Set the response content type to HTML
        response.headers['Content-Type'] = 'text/html'
        response.body = html_content.encode('utf-8')

# Run the application
web_app.run()
```

4. Run your web application:

```
python app.py
```

Your WebPy application is now running at `http://127.0.0.1:8080/`.

## Contributing

MicroWeb is an open-source project developed and maintained by the community. Contributions are welcome and encouraged! If you'd like to contribute, please check out our [contribution guidelines](CONTRIBUTING.md).

## Support

For help or questions about MicroWeb, please visit our [GitHub repository](https://github.com/webpy/webpy) or join our [community chat](https://discord.gg/D4gsQG7hmU).

## License

WebPy is released under the GLP-3.0 License. See [LICENSE](LICENSE) for details.

