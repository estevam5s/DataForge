"""
DataForge Programming Language - Setup
A revolutionary programming language built on Python.
"""

from setuptools import setup, find_packages

setup(
    name="dataforge-lang",
    version="2.0.0",
    description="DataForge - A revolutionary programming language built on Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="DataForge Team",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "dataforge=dataforge.cli:main",
            "df=dataforge.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
    ],
)
