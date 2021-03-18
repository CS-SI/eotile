# 🛰️ EOTile

[![Version](https://img.shields.io/badge/Version-0.1-g)]() [![Python](https://img.shields.io/badge/Python-3.6+-blue)]()

Managed Sentinel-2 and Landsat8 tiles

## ⏬ Installation

Install the package using pip:
```sh
git clone https://gitlab.cloud-espace.si.c-s.fr/RemoteSensing/eotile.git
cd eotile
pip install .
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
* `-s2_only`              output S2 tiles and not the L8 ones
* `-l8_only`              output L8 tiles and not the S2 ones
* `-srtm`                 Use SRTM tiles as well
* `-cop`                  Use Copernicus tiles as well

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
[S2_Tiles, L8_Tiles, SRTM_Tiles, Copernicus_Tiles] = eotile_module.main("Spain", l8_only=True) 
# Replace Spain with whatever string you might need (a file, a tile id, a location, a wkt polygon, a bbox)

# Returned elements are GeoPandas Dataframes :
print(S2_Tiles.id)

# Iter over the Dataframe :
for tile in L8_Tiles.iterrows():
    print(tile[1].geometry.wkt)

```

## 🔖 Examples

* Using a location
```sh
eotile "Metropolitan+France" -threshold 1 -to_tile_id
```
* Using a BBOX
```sh
eotile "0.49593622377, 43.326246335, 1.7661878622, 44.246370915" -s2_only -logger_file test.log
```
(This line will produce an output under the test.log file)
* Using a wkt
```sh
eotile 'POLYGON ((0.8468214953196805 44.02363566574142, 0.84638 44.0237, 0.8590044453705752 44.06127355906579, 0.8712896362539795 44.09783741052559, 1.325549447552162 45.44983010010615, 1.338016257992888 45.48693449754356, 1.35047 45.524, 1.350948946138455 45.52393017672913, 3.65866 45.1875, 3.644501621308357 45.14977803391441, 3.111537654412643 43.72980975068511, 3.09866 43.6955, 0.8468214953196805 44.02363566574142))' -to_location -l8_only
```
* Using a S2 tile id
```sh
eotile 31TCJ -to_file data/TLS_tiles.shp
```
* Using a file
```sh
eotile tests/test_data/illinois.shp -s2_only -vvv
```

## 👁️‍🗨️ Data sources & Licenses

* **SRTM**
```
Vector grid of SRTM 1x1 degree tiles
https://figshare.com/articles/dataset/Vector_grid_of_SRTM_1x1_degree_tiles/1332753

Vector file (shapefile format) of polygons representing the 1x1 degree tiles of SRTM (3-arcsec and 1-arcsec). There are 14280 polygons with an ID that matches the naming scheme of SRTM (such as N00E025). Lat/Long, WGS84. 
```

* **Copernicus**
```
s3://copernicus-dem-30m/grid.zip
GLO-30 Public and GLO-90 are available on a free basis for the general public under the terms and conditions of the Licence found here:
https://spacedata.copernicus.eu/documents/20126/0/CSCDA_ESA_Mission-specific+Annex.pdf

See
https://github.com/CS-SI/eodag/blob/develop/examples/tuto_cop_dem.ipynb
```
