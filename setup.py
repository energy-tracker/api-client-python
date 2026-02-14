"""Setup configuration for energy-tracker-api package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="energy-tracker-api",
    version="2.0.0",
    author="Stefan Nebel",
    description="Async Python client for Energy Tracker API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/energy-tracker/api-client-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.14",
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.24.0",
            "pytest-cov>=4.0.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
        ],
    },
)
