import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dj-commented-view",
    version="0.1.0",
    author="Skye Im",
    author_email="skye.im@nyu.edu",
    description="PCTNet internal class for comments on other models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skairunner/dj-commented-view",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
