from app import WebPyApp


# Instantiate the WebPyApp wrapper
web_app = WebPyApp()

# Define a route and corresponding handler function
@web_app.route("/hello", methods=['GET', 'POST'])
def hello(request, response):
    if request.method == 'GET':
        name = request.query_params.get('name', 'Guest')
        response.body = f"Hello, {name}!".encode('utf-8')
    elif request.method == 'POST':
        data = request.json()
        if 'name' in data:
            response.json({'message': f"Hello, {data['name']}!"})
        else:
            response.json({'error': 'Name not provided'}), 400


# Run the application
web_app.run()
