# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS GROUP - France.
#
# This file is part of EOTile.
# See https://github.com/CS-SI/eotile for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Generate tile list according AOI

:author: msavinaud; mgerma
:organization: CS GROUP - France 
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eotile",
    version="0.2.6",
    description="Managed Sentinel-2 and Landsat8 tile",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Mickaël Savinaud, Mathis A. Germa",
    author_email="mickael.savinaud@csgroup.eu, mathis.germa@csgroup.eu",
    url="https://github.com/CS-SI/eotile",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.6, <4",
    license="Apache License Version 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "geopandas>= 0.9,<0.10",
        "geopy>=2.2,<3",
        "pyproj>=3,<4",
        "requests<=2.26,<3",
        "Shapely>=1.7,<2",
    ],
    include_package_data=True,
    package_data={
        "": [
            "data/aux_data/s2_no_overlap.gpkg",
            "data/aux_data/s2_with_overlap.gpkg",
            "data/aux_data/l8_tiles.gpkg",
            "data/aux_data/DEM_Union.gpkg",
            "data/aux_data/srtm5x5_tiles.gpkg",
            "config/data_path",
        ]
    },
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage>5,<=6"],
    },
    entry_points={
        "console_scripts": [
            "eotile=eotile.eotile_cli:main",
        ],
    },
)
