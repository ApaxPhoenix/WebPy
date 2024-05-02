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

1. Install MicroWeb using pip:

```
pip install webpy
```

2. Create a new Python file for your web application, e.g., `app.py`.

3. Write your web application code using MicroWeb's simple routing system.

```python
from webpy import WebPy

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

