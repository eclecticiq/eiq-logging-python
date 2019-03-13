import setuptools

setuptools.setup(
    name="eiq-logging",
    version="1.3",
    packages=setuptools.find_packages(include=["eiq_logging", "eiq_logging.*"]),
    data_files=["LICENSE"],
    install_requires=["structlog"],
    description="Consistent logging for EIQ projects.",
    author="EclecticIQ",
    author_email="opensource@eclecticiq.com",
    url="https://github.com/eclecticiq/eiq-logging-python",
    license="BSD-3-Clause",
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ],
)
