# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: msavinaud; mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

from setuptools import find_packages, setup

setup(
    name="eotile",
    version="0.1",
    description="Managed Sentinel-2 and Landsat8 tile",
    author="Mickaël Savinaud, Mathis A. Germa",
    author_email="mickael.savinaud@csgroup.eu, mathis.germa@csgroup.eu",
    license="Copyright (c) 2021 CS Group, Tous droits réservés",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.6, <4",
    install_requires=[
        "shapely",
        "fiona",
        "geopy",
        "pyproj",
        "geopandas",
        "lxml",
        "geopy",
        "requests",
    ],
    include_package_data=True,
    package_data={
        "": [
            "data/aux_data/s2_no_overlap.gpkg",
            "data/aux_data/l8_tiles.gpkg",
            "data/aux_data/cop_tiles.gpkg",
            "data/aux_data/srtm_tiles.gpkg",
            "config/data_path",
        ]
    },
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "eotile=eotile.eotile_cli:main",
        ],
    },
)
