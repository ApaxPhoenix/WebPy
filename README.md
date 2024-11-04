# WebPy: Pythonic Web Development

An experimental framework for fast web development in Python. Develop simple and responsive web apps with ease.

## Why Choose WebPy?

- **Minimalistic**: Build your application with no unneeded bells and whistles.
- **Simple Structure**: Clean and straightforward setup to ensure ease of organization and maintenance.
- **Flexible Dependencies**: Use whatever other packages you like—none are mandated for you.
- **Scalable & Extensible**: Start with a functioning project and scale up. Extensible by adding required features whenever needed.

## Getting Started

Setting up WebPy takes very few steps:

1. **Installation**

   Install WebPy using pip:

   ```bash
   pip install webpy
   ```

2. **Write Your Web Application**

   Create a Python file (`app.py`) and start coding:

   ```python
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
   ```

3. **Run Your Web Application**

   Execute your script:

   ```bash
   python app.py
   ```

   Your application will be running on `http://127.0.0.1:8080/`, served by WebPy.

## License

WebPy is published under the MIT License. See [LICENSE](LICENSE) for details.
