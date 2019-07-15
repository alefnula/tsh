import io
import setuptools


version = "0.0.1"
author = "Viktor Kerkez"
author_email = "alefnula@gmail.com"
url = "https://github.com/alefnula/tsh"


setuptools.setup(
    name="tsh",
    version="0.0.1",
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    description="tea-shell - execute command line tools like python functions,"
    " while you sit back and sip on your tea.",
    long_description=io.open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url=url,
    platforms=["Windows", "POSIX", "MacOSX"],
    license="Apache-2.0",
    packages=setuptools.find_packages(),
    install_requires=io.open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
