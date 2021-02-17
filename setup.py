# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(

    name='eotile',  
    
    version='0.0.1',

    description='Managed Sentinel-2 and Landsat8 tile', 

    author='Mickaël Savinaud, Mathis A. Germa',

    author_email='mickael.savinaud@csgroup.eu, mathis.germa@csgroup.eu', 
    license="Copyright (c) 2021 CS Group, Tous droits réservés",

    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires='>=3.6, <4',

    install_requires=['GDAL'],

    extras_require={ 
        'dev': ['check-manifest', 'geopandas'],
        'test': ['coverage'],
    },

    
    entry_points={  
        'console_scripts': [
            'eotile=eotile.eotile_cli:main',
        ],
    },
)
