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


## Running tests

You need additionnal packages in order to run the tests:
```sh
pip install ".[dev]"
```

In order to run the test, you can use the following command:
```sh
python tests/test_create_tiles_file_from_AOI.py
```
