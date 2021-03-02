# EOTile
[![Version](https://img.shields.io/badge/Version-1.0.0-g)]() [![Python](https://img.shields.io/badge/Python-3.6+-blue)]()


### 🛰️ Managed Sentinel-2 and Landsat8 tiles

## 📡 Installation

Install the package using pip:
```sh
git clone https://gitlab.cloud-espace.si.c-s.fr/RemoteSensing/eotile.git
cd eotile
pip install .
```

## 📁 Usage

```sh
eotile [from] [to]
```

from options :
* file              Get tiles that corresponds to an AOI contained in a shapefile
* tile_id           Get tiles that corresponds to a specific tile id
* location          Get tiles that corresponds to a location (from Nominatim)
* wkt               Get tiles that corresponds to an AOI designated by its wkt
* bbox              Get tiles that corresponds to an AOI designated by its four coordinates

to options :
* -None                 Output all infos on standard output
* -to_file TO_FILE      Write tiles to a file
* -to_wkt               Output the geometry of matching tiles with wkt format on standard output
* -to_bbox              Output the bounding box of matching tiles on standard output
* -to_tile_id           Output the id(s) of matching tiles on standard output
* -to_location          Output the location of the centroid of matching tiles on standard output


Other options :
* -s2_only              output S2 tiles which intersect the aoi
* -l8_only              output L8 tiles which intersect the aoi
* -log_level		    Level of the logging system, default is warn : Amongst [debug, info, warn, error]
* -epsg                 Specify the epsg of the input if not WGS84


Examples :

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
## Running tests

You need additionnal packages in order to run the tests:
```sh
pip install ".[dev]"
```

In order to run the test, you can use the following command:
```sh
python tests/test_create_tiles_file_from_AOI.py
```
