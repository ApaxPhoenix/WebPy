from webpy import WebPy

# Creating the WebPyApp wrapper
web_app = WebPy()

# Define router and handler function
@web_app.route('/hello', methods=['GET'])
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
    # Set content type in response header
    response.headers['Content-Type'] = 'text/html'
    response.body = html_content.encode('utf-8')

# Run the application
web_app.run()