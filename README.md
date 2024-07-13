# WebPy: Simplified Web Development in Python

WebPy is an experimental Python framework designed for streamlined web development. Build lightweight and efficient web applications effortlessly.

## Why Choose WebPy?

- **Minimalist Approach**: Focus on building your application without unnecessary complexity.
- **Simple Structure**: Clean and straightforward setup for easy organization and maintenance.
- **Flexible Dependencies**: Choose the dependencies that best suit your needs—no enforced packages.
- **Scalable and Extensible**: Start small and scale up as your project grows. Easily extendable with community-provided extensions.

## Getting Started

Get up and running with WebPy in just a few simple steps:

1. **Installation**

    Install WebPy using pip:

    ```bash
    pip install webpy
    ```

2. **Write Your Web Application**

    Create a Python file (e.g., `app.py`) and start coding:

    ```python
    from webpy import WebPy

    # Instantiate the WebPyApp wrapper
    web_app = WebPy()

    # Define a route and corresponding handler function
    @web_app.route("/hello", methods=['GET'])
    def hello(request, response):
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

3. **Run Your Web Application**

    Execute your script:

    ```bash
    python app.py
    ```

    Your WebPy application will be running at `http://127.0.0.1:8080/`.

## License

WebPy is released under the MIT License. See [LICENSE](LICENSE) for details.
