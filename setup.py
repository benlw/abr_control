#!/usr/bin/env python

# Automatically generated by nengo-bones, do not edit this file directly

import io
import pathlib
import runpy

try:
    from setuptools import find_packages, setup
except ImportError:
    raise ImportError(
        "'setuptools' is required but not installed. To install it, "
        "follow the instructions at "
        "https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py"
    )


def read(*filenames, **kwargs):
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


root = pathlib.Path(__file__).parent
version = runpy.run_path(str(root / "abr_control" / "version.py"))["version"]

install_req = [
    "cloudpickle>=0.8.0",
    "cython>=0.29.0",
    "matplotlib>=3.0.0",
    "numpy>=1.16.0",
    "setuptools>=18.0",
    "scipy>=1.1.0",
    "sympy>=1.3",
]
docs_req = []
optional_req = []
tests_req = [
    "pytest>=4.4.0",
    "pytest-xdist>=1.26.0",
    "pytest-cov>=2.6.0",
    "pytest-plt",
    "coverage>=4.5.0",
    "nengo>=2.8.0",
]

setup(
    name="abr-control",
    version=version,
    author="Applied Brain Research",
    author_email="travis.dewolf@appliedbrainresearch.com",
    packages=find_packages(),
    url="https://github.com/abr/abr_control",
    include_package_data=False,
    license="Free for non-commercial use",
    description="Robotic arm control in Python",
    long_description=read("README.rst", "CHANGES.rst"),
    zip_safe=False,
    install_requires=install_req,
    extras_require={
        "all": docs_req + optional_req + tests_req,
        "docs": docs_req,
        "optional": optional_req,
        "tests": tests_req,
    },
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: ABR Control",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
