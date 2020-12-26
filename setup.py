# standard library
import os

# pypi library
from setuptools import find_packages, setup

version = os.getenv("VERSION")

if not version:
    print(
        "Please use `make build` to build the package. Or manually `export VERSION=xxx` and rerun"
    )

requirements = [
    'click==7.1.2; (python_version >= "2.7" and python_full_version < "3.0.0") or (python_full_version >= "3.5.0")'
]

setup(
    name="req2toml",
    version=version,
    description="Convert requirements.txt to pyproject.toml",
    author="Ben Chen",
    author_email="bn@benbenbang.io",
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=["poetry", "python", "convert", "requirements"],
    packages=find_packages(exclude=["doc", "tests*"]),
    include_package_data=False,
)
