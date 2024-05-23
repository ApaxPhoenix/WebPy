# WebPy: Simplified Web Development in Python

WebPy is an experimental Python framework designed to streamline web development with its minimalist approach. Build lightweight and efficient web applications effortlessly.

## Why Choose WebPy?

- **Minimalist Approach**: WebPy provides a lightweight and simplified framework for web development, allowing you to focus on building your application without unnecessary complexity.

- **Simplified Project Structure**: Say goodbye to convoluted project structures. With WebPy, you get a clean and straightforward setup, making it easier to organize and maintain your code.

- **No Enforced Dependencies**: WebPy lets you choose the dependencies you need for your project. There are no enforced dependencies, giving you the freedom to use the tools that best suit your needs.

- **Scalability and Extensibility**: Start small and scale up as your project grows. WebPy is designed to be easily extendable with community-provided extensions, allowing you to add new features and functionality with ease.

## Getting Started

Get up and running with WebPy in just a few simple steps:

1. **Installation**

    Install WebPy using pip:

    ```bash
    pip install webpy
    ```

2. **Write Your Web Application**

    Create a Python file for your web application, such as `app.py`, and start coding using WebPy's simple routing system:

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

    Execute your web application script:

    ```bash
    python app.py
    ```

    Your WebPy application is now running at `http://127.0.0.1:8080/`.

## Want to Contribute?

WebPy is an open-source project driven by the community. Join us in shaping the future of web development with Python. Check out our [contribution guidelines](CONTRIBUTING.md) to get started.

## Need Help?

Have questions or need assistance with WebPy? Visit our [GitHub repository](https://github.com/webpy/webpy) or join our [community chat](https://discord.gg/webpy) for support.

## License

WebPy is released under the GPL-3.0 License. See [LICENSE](LICENSE) for details.
