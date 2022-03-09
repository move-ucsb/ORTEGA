import os
import re
from setuptools import setup


with open("ortega/__init__.py", "r") as file:
    contents = file.read()


def meta(name):
    pattern = re.compile(rf"__{name}__ = \"(.*)\"")
    val = re.findall(pattern, contents)
    return val[0]


if __name__ == "__main__":
    setup(
        name=meta("title"),
        version=meta("version"),
        author=meta("author"),
        packages=["ortega"],
        url=meta("url"),
        license=meta("license"),
        description=meta("description"),
        install_requires=[
            "numpy",
            "pandas",
            "shapely",
            "attrs",
            "matplotlib",
            "statistics",
        ],
    )
