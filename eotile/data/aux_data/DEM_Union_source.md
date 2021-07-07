
# source files:
* Copernicus:
(A) https://spacedata.copernicus.eu/fr/dataset-details?articleId=394198
* SRTM:
(B) For tile ids: https://figshare.com/articles/dataset/Vector_grid_of_SRTM_1x1_degree_tiles/1332753
(C) For restriction (trusted source):
https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-void?qt-science_center_objects=0#qt-science_center_objects

Building output data out of the source files:


# Steps:
* Remove the following tiles from (B):
  - N59E170
  - S11W139
  - N27E012
(Building the (B)-(C) and (C)-(B) difference explains that step)
* rename (B) id column to SRTM_GEOM_CELL_ID
* Use QGIS `Union` tool to merge layers (A) and (B)
* Delete all polygons that have an area of 0
(This can be done by adding a field _area with `$area` value in it, then select polygons by filtering _area value equals 0, then clicking `remove selected features`)
* Create new fields `EXIST_...`
Click `Open attribute table` then `field calculator`. Choose `create new field` and name it  `EXIST_...`. Select Type Boolean.
The expression is the following:
  - for `EXIST_SRTM`: if(SRTM_GEOM_CELL_ID is not NULL, True, False)
  - for `EXIST_COP30`: if(Product10 is not NULL, True, False)
  - for `EXIST_COP90`: if(Product30 is not NULL, True, False)
* `Id` and `fid` columns have to be deleted in order to export in .gpkg format


Checks: 
* The new layer should contain 26481 features.
* There are no features where SRTM_GEOM_CELL_ID is different from GEOM_CELL_ID (excepted NULL case)
