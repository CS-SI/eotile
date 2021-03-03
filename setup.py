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
    version="1.0.0",
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
        "requests"
    ],
include_package_data = True,
    package_data={'': ['data/aux_data/wrs2_descending/wrs2_descending.dbf',
'data/aux_data/wrs2_descending/wrs2_descending.prj',
'data/aux_data/wrs2_descending/wrs2_descending.sbn',
'data/aux_data/wrs2_descending/wrs2_descending.sbx',
'data/aux_data/wrs2_descending/wrs2_descending.shp',
'data/aux_data/wrs2_descending/wrs2_descending.shx',
'data/aux_data/S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml',
'config/data_path']},
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
