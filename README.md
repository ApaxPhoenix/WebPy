# CrawlPy

CrawlPy is a lightweight Python library for web crawling, making it easy to fetch and process web content efficiently.

## Introduction

CrawlPy simplifies the process of web crawling by providing a minimalist framework for fetching and parsing web pages in Python.

## Features

- Lightweight and minimalist
- Simple API for making HTTP requests
- Flexible enough to handle various crawling tasks
- Support for handling cookies and custom headers

## Getting Started

To get started with CrawlPy, follow these simple steps:

1. Install CrawlPy using pip:

```bash
pip install crawlpy
```

2. Create a new Python file for your crawler, e.g., `crawler.py`.

3. Write your crawling logic using CrawlPy's easy-to-use API.

```python
from crawlpy import CrawlPy
       
# Create a CrawlPy instance
crawler = CrawlPy()

# Make a GET request
response = crawler.get('https://example.com/resource')

# Check the response status code
print("Status Code:", response.status)

# Read the response content
content = response.content.decode('utf-8')
print("Response Content:", content)

# Close the connections when done
crawler.close()
```

4. Run your crawler:

```bash
python crawler.py
```

Your CrawlPy crawler is now fetching web content!

## Contributing

CrawlPy is an open-source project developed and maintained by the community. Contributions are welcome and encouraged! If you'd like to contribute, please check out our [contribution guidelines](CONTRIBUTING.md).

## Support

For help or questions about CrawlPy, please visit our [GitHub repository](https://github.com/crawlpy/crawlpy) or join our [community chat](https://discord.gg/CrawlPy).

## License

CrawlPy is released under the GLP-3.0 License. See [LICENSE](LICENSE) for details.
