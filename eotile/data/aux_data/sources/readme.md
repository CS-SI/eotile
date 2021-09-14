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
This file contains information about where does the data sources comes from.

In order to get these data, you can use eotile-converter

## S2 Tiles with overlap

The S2 Tiles system comes from [S1 Tiling ressources](https://gitlab.orfeo-toolbox.org/s1-tiling/s1tiling/-/tree/develop/s1tiling/resources/shapefile)
It has been converted to the required format using QGIS 3.14 by the following steps:
- Load the Features.shp shapefile with QGIS
- **Toggle** on **Editing** of the layer
- Open the **attribute table** (F6)
- Add a new field (Ctrl+W)
- Name this new field "id" and type Text (String)
- Update this field using the **Field Calculator**
- Select "Update existing field" then select the newly created id field
- In the expression text area, type **Name**. Then check that the feature corresponds to tile ids in the Preview.
- If the preview matches the tile ids, click Ok.
- Save the layer changes and **Toggle** off **Editing** of the layer
- You can now export the layer. Right click on the layer, under Export select Save Features as
  * on format select GeoPackage
  * on filename : **[eotile_path]**/eotile/data/aux_data/s2_with_overlap.gpkg
  * on Layer name : s2_with_overlap
  * CRS : EPSG: 4326 WGS 84
  * Encoding UTF-8
  * fields to export : select only the "id" field
- Leave the rest as it is by default and click "Ok"
