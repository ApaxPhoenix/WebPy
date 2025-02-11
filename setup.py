from setuptools import setup, find_packages

setup(
    name="WebPy",
    version="0.1.0",
    author="Andrew Hernandez",
    author_email="andromedeyz@hotmail.com",
    description="A web framework for building Python applications with ease.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://localhost:3000/pi/WebPy",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Natural Language :: English"
    ],
    python_requires=">=3.9",
)