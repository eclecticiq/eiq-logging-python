import os
import setuptools

# allow setup.py to be ran from anywhere
os.chdir(os.path.dirname(os.path.abspath(__file__)))

setuptools.setup(
    name="eiq-logging",
    version="1.4",
    packages=setuptools.find_packages(include=["eiq_logging", "eiq_logging.*"]),
    data_files=["LICENSE"],
    install_requires=["structlog"],
    description="Consistent logging for EIQ projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="EclecticIQ",
    author_email="opensource@eclecticiq.com",
    url="https://github.com/eclecticiq/eiq-logging-python",
    license="BSD-3-Clause",
    classifiers=["License :: OSI Approved :: BSD License"],
)
