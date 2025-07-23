from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in laundrycloud/__init__.py
from laundrycloud import __version__ as version

setup(
    name="laundrycloud",
    version=version,
    description="Comprehensive Laundry Management System for ERPNext",
    author="LaundryCloud",
    author_email="info@laundrycloud.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)