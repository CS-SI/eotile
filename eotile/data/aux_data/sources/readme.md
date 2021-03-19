<!--
Copyright (c) 2021 CS Group.

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

