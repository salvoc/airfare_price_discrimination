# Airfare price discrimination analysis

This project consists of a number of Selenium-based web scrapers, a parser and a CLI interface all written in Python.
The scrapers dump search results in form of html wrapped sources and in parallel as PNG screenshots, to allow multiple parsing approaches.

The all ACI folder should be built as a Docker image as specified in the Dockerfile.

Once the image is created, it can be instantiated in form of a single docker container and the CLI endpoints can be used as startup commands.

The scrapers are enhanced by a class that triggers low level Selenium events to simulate human behaviour clicks and typing.

The parser is based on Bautifulsoup, the scrapers on Selenium, all of the requirements are contained in the requirements.txt file.

