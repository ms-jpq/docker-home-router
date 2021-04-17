#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_packages, setup

packages = find_packages(exclude=("tests*",))
package_data = {pkg: ("py.typed", "*.html", "*.conf") for pkg in packages}
install_requires = Path("requirements.txt").read_text().splitlines()

setup(
    name="router",
    python_requires=">=3.8.0",
    install_requires=install_requires,
    version="0.0.1",
    description="Router",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="ms-jpq",
    author_email="github@bigly.dog",
    url="https://github.com/ms-jpq/router",
    packages=packages,
    package_data=package_data,
)
