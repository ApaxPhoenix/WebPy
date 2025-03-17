from setuptools import setup, find_packages

# setuptools configuration for packaging the WebPy framework
setup(
    # Basic package metadata
    name="WebPy",  # Package name as it will appear on PyPI
    version="0.1.0",  # Semantic versioning (major.minor.patch)
    author="Andrew Hernandez",  # Primary author/maintainer
    author_email="andromedeyz@hotmail.com",  # Contact email for inquiries
    
    # Package descriptions
    description="A web framework for building Python applications with ease.",  # Short description
    long_description=open("README.md").read(),  # Full description from README.md file
    long_description_content_type="text/markdown",  # Format of the long description
    
    # Project homepage or repository URL
    url="http://github.com/ApaxPhoenix/WebPy",  # Current repo URL
    
    # Package discovery and inclusion
    packages=find_packages(),  # Automatically find all packages in the project
    
    # Dependencies
    # Read requirements from requirements.txt file to maintain a single source of truth
    install_requires=open("requirements.txt").read().splitlines(),
    
    # Package metadata for PyPI
    classifiers=[
        "Programming Language :: Python :: 3",  # Python version compatibility
        "License :: OSI Approved :: MIT License",  # License type
        "Operating System :: OS Independent",  # OS compatibility
        "Development Status :: 3 - Alpha",  # Development phase indicator
        "Intended Audience :: Developers",  # Target users
        "Topic :: Internet :: WWW/HTTP",  # Framework category
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",  # Framework capability
        "Topic :: Software Development :: Libraries :: Python Modules",  # Framework type
        "Topic :: Software Development :: Libraries :: Application Frameworks",  # Framework purpose
        "Natural Language :: English"  # Documentation language
    ],
    
    # Minimum Python version required
    python_requires=">=3.9",  # Requires Python 3.9 or newer for typing features
)
