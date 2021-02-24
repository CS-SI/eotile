# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="eotile",
    version="1.0.0",
    description="Managed Sentinel-2 and Landsat8 tile",
    author="Mickaël Savinaud, Mathis A. Germa",
    author_email="mickael.savinaud@csgroup.eu, mathis.germa@csgroup.eu",
    license="Copyright (c) 2021 CS Group, Tous droits réservés",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.6, <4",
    install_requires=["GDAL","lxml"],
    extras_require={
        "dev": ["check-manifest", "geopandas"],
        "test": ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "eotile=eotile.eotile_cli:main",
        ],
    },
)
