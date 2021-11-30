<!--
Copyright (c) 2021 CS GROUP - France.

This file is part of EOTile.
See https://github.com/CS-SI/eotile for further info.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
# 🛰️ EOTile

[![Version](https://img.shields.io/badge/Version-0.2.7-g)]() [![Python](https://img.shields.io/badge/Python-3.6+-blue)]()

EOTile is a tile grid management tool that provide quick and easy methods to grab tile ids or information about its footprint.
There are four grid systems currently supported : 
 * The one used by **Landsat 8**
 * The one used by **Sentinel 2**
 * The standard for **DEM** tiles
 * The specific one used by many SRTM providers gathering 5x5 tiles


## ⏬ Installation

Install the package using pip:
```sh
pip install eotile
```

## 🔲 Usage

### 📟 Through the CLI
```sh
eotile [input] [output]
```

You can **input** these elements : a file, a tile id, a location, a wkt polygon, a bbox

### To options (Optional):
* `-to_file FILE_PATH`      Write tiles to a *geography* file
* `-to_wkt`               Output the geometry of matching tiles with wkt format on standard output
* `-to_bbox`              Output the bounding box of matching tiles on standard output
* `-to_tile_id`           Output the id(s) of matching tiles on standard output
* `-to_location`          Output the location of the centroid of matching tiles on standard output

### Tiles selection :
* `-no_l8`              output S2 tiles and not the L8 ones
* `-no_s2`              output L8 tiles and not the S2 ones
* `-s2_overlap`         Use S2 tiles with overlap
* `-dem`                Use elevation tiles as well
* `-srtm5x5`            Use specific 5x5 SRTM tiles as well

##### Other options :
* `-epsg`                 Specify the epsg of the input if not WGS84
* `-logger_file LOGGER_FILE_PATH` Redirect information from standard output to a file
* `-location_type {city, county, state, country}` If needed, specify the location type that is requested
                        
* `-threshold THRESHOLD` For large polygons at high resolution, you might want
                        to simplify them using a threshold (0 to 1)
* `-min_overlap MIN_OVERLAP` Minimum percentage of overlap to consider a tile (0 to 1)

### 🐍 Through the python module

Getting Started :
```python
# Import the module
from eotile import eotile_module 

# Create tile lists
[S2_Tiles, L8_Tiles, DEM_Tiles, SRTM5x5_Tiles] = eotile_module.main("Spain", no_s2=True) 
# Replace Spain with whatever string you might need (a file, a tile id, a location, a wkt polygon, a bbox)

# Returned elements are GeoPandas Dataframes :
print(S2_Tiles.id)

# Iter over the Dataframe :
for tile in L8_Tiles.iterrows():
    print(tile[1].geometry.wkt)

```

You can also use the advanced quicksearch

```python
# Import the module
from eotile.eotile_module import quick_search 

# Create the GeoPandas DataFrame of L8 Tiles corresponding to this S2 Tile id 
gdf = quick_search("31TCJ", "tile_id", "L8")
>>     id                                           geometry
0  198029  POLYGON ((0.84682 44.02364, 0.84638 44.02370, ...
1  199029  POLYGON ((-0.69823 44.02364, -0.69866 44.02370...
2  199030  POLYGON ((-0.86579 42.55300, -1.13296 42.59191...
3  198030  POLYGON ((0.67927 42.55300, 0.41210 42.59191, ...
```
*Note: quick_search uses OGR for a quicker result. This requires a proper installation of GDAL components*
## 🔖 Examples

* Using a location
```sh
eotile "Metropolitan France" -threshold 1 -to_tile_id
```
* Using a BBOX
```sh
eotile "0.49593622377, 43.326246335, 1.7661878622, 44.246370915" -no_l8 -logger_file test.log
```
(This line will produce an output under the test.log file)
* Using a wkt
```sh
eotile 'POLYGON ((0.8468214953196805 44.02363566574142, 0.84638 44.0237, 0.8590044453705752 44.06127355906579, 0.8712896362539795 44.09783741052559, 1.325549447552162 45.44983010010615, 1.338016257992888 45.48693449754356, 1.35047 45.524, 1.350948946138455 45.52393017672913, 3.65866 45.1875, 3.644501621308357 45.14977803391441, 3.111537654412643 43.72980975068511, 3.09866 43.6955, 0.8468214953196805 44.02363566574142))' -to_location -no_s2
```
* Using S2 tile ids
```sh
eotile "31TCJ, 31TCE" -to_file data/TLS_tiles.shp
```
* Using a file
```sh
eotile tests/test_data/illinois.shp -no_l8 -vvv
```

## 👁️‍🗨️ Data sources & Licenses

* **SRTM 5x5**
```
Vector grid of Specific SRTM 5x5 degree tiles
See issue #39 to download 
```

* **DEM**

See [DEM_Union_source](eotile/data/aux_data/DEM_Union_source.md)


## 🆘 Help and Troubleshoot

See https://www.gaia-gis.it/fossil/libspatialite/tktview/760ef1affb822806191393ac3f208fc9d8647758

* Note that the number of Tiles of S2 without overlap and with overlap is not the same. The difference apparently lies in the Geodesic line break north and south corners. 
  - S2 without overlap: 56686 Tiles
  - S2 with ouverlap:   56984 Tiles

