from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="vvvvid-downloader",
    version="1.1.2",
    author="Nearata",
    author_email="williamdicicco@protonmail.com",
    description="Uno script in Python che permette di scaricare facilmente i video da VVVVID.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nearata/vvvvid-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: Italian",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console"
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests==2.24.0",
        "inquirer==2.7.0",
        "colorama==0.4.3"
    ]
)
