"""Setup pyNetia package."""

from setuptools import setup
from pyNetia import _VERSION_ as version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'pyNetia',
    packages = ['pyNetia'],
    version = version,
    license = 'gpl-3.0',
    description = 'Python wrapper for Netia Player',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = 'Jakub Orasiński',
    author_email = 'korasinski@icloud.com',
    url = 'https://github.com/korasinski/pyNetia',
    keywords = ['Netia Player', 'Home Assistant', 'custom component'],
    install_requires =['requests'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
)
