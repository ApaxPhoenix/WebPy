from setuptools import setup, find_packages

setup(
    name='WebPy',
    version='0.1.0',
    author='Andrew Hernandez',
    author_email='andromedeyz@hotmail.com',
    description='A brief description of your library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ApaxPhoenix/WebPy',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here, e.g. 'numpy', 'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
