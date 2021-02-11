

from setuptools import setup, find_packages
import pathlib

setup(

    name='EOTile',  
    
    version='0.0.1',  # Required

    description='Managed Sentinel-2 and Landsat8 tile', 

    author='Mickaël Savinaud, Mathis A. Germa',

    author_email='mickael.savinaud@csgroup.eu, mathis.germa@csgroup.eu', 
    license="Copyright (c) 2021 CS Group, Tous droits réservés",

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={'': 'eotile'},  # Optional

    packages=find_packages(where='eotile'),  
    python_requires='>=3.6, <4',

    install_requires=['GDAL'],

    extras_require={ 
        'dev': ['check-manifest', 'geopandas'],
        'test': ['coverage'],
    },

    
    entry_points={  
        'console_scripts': [
            'eodag=eotile_cli:main',
        ],
    },
)
