This file contains information about where does the data sources comes from.

## S2 Tiles from xml file

To get the gpkg file from xml data, you'll need to checkout the **xml_cutter** branch.
This branch will also work for the other data sources

eotile "POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))" -s2_only -to_file eotile/data/aux_data/s2/s2_no_overlap.gpkg 

(Feature Count: 34355) -> OK with xml_s2_output.log

## L8 Tiles from shp

eotile "POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))" -l8_only -to_file eotile/data/aux_data/l8/l8_tiles.gpkg 

- 28892 L8 Tiles

## Copernicus Tiles from shp

eotile "POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))" -l8_only -to_file eotile/data/aux_data/cop_tiles.gpkg -s2_only -cop

- 64800 Copernicus Tiles

## SRTM Tiles from shp

eotile "POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))" -l8_only -to_file eotile/data/aux_data/srtm_tiles.gpkg -s2_only -srtm

- 14280 SRTM Tiles

