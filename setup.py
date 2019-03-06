import setuptools

setuptools.setup(
    name="eiq-logging",
    version="1.2",
    packages=setuptools.find_packages(include=["eiq_logging", "eiq_logging.*"]),
    install_requires=["structlog"],
)
