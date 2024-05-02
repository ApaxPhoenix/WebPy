from wrapper import WebPyApp

# Instantiate the WebPyApp wrapper
web_app = WebPyApp()

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
