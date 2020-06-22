import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="big-small-rss-notifier", # Replace with your own username
    version="0.3.0",
    author="Lauri Jakku",
    author_email="lja@iki.fi",
    description="RSS Notifier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MiesSuomesta/big-small-rss-notifier",
    packages=setuptools.find_packages(include=['*.py']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.6',
)

