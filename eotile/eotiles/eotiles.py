# -*- coding: utf-8 -*-
"""
tile list utilities

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import pathlib
from lxml import etree as ET

from osgeo import ogr, osr

from eotile.eotile.eotile import EOTile, L8Tile, S2Tile

# mypy imports
from typing import List, Optional, Union

LOGGER = logging.getLogger(__name__)


def write_tiles_bb(tile_list: Union[List[S2Tile],
                                    List[L8Tile]], filename: str, sensor="S2"):
    """Writes the input tiles to a file

    :param tile_list: The list of input tiles to write
    :type tile_list: list
    :param filename: Path to the output file aux data (Must be a shp file)
    :type filename: String
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(filename)
    if pathlib.Path(filename).exists():
        driver.DeleteDataSource(filename)

    # create the spatial reference for the bounding box, WGS84
    srs_bb = osr.SpatialReference()
    srs_bb.ImportFromEPSG(4326)
    # create the layer
    layer_bb = data_source.CreateLayer("bb", srs_bb, ogr.wkbPolygon)

    # Add the fields
    field_name = ogr.FieldDefn("TileID", ogr.OFTString)
    field_name.SetWidth(10)
    layer_bb.CreateField(field_name)

    for tile in tile_list:
        feature = ogr.Feature(layer_bb.GetLayerDefn())
        feature.SetField("TileID", tile.ID)
        feature.SetGeometry(tile.polyBB)
        layer_bb.CreateFeature(feature)
        feature.Destroy()

    data_source.Destroy()


def create_tiles_list_S2(filename_tiles_list: str, filename_aoi: str) -> Optional[List[S2Tile]]:
    """Create the S2 tile list according to an aoi

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: String
    """
    # Open the tiles list file
    tree = ET.parse(filename_tiles_list)
    root = tree.getroot()

    driver = ogr.GetDriverByName("ESRI Shapefile")

    # Open the AOI file
    dataSource_aoi = driver.Open(filename_aoi, 0)
    # Check to see if shapefile is found.
    if dataSource_aoi is None:
        LOGGER.error("ERROR: Could not open {}".format(filename_aoi))
        raise IOError

    layer_aoi = dataSource_aoi.GetLayer()
    featureCount = layer_aoi.GetFeatureCount()
    if featureCount != 1:
        LOGGER.error(
            "ERROR: Number of features in {}: {}".format(
                pathlib.Path(filename_aoi).name, featureCount
            )
        )
        raise AssertionError

    # Get the first feature
    feature_aoi = layer_aoi.GetNextFeature()

    tile_list = []
    tile_dateline = 0
    for tile_elt in root.findall("./DATA/REPRESENTATION_CODE_LIST/TILE_LIST/TILE"):
        tile = S2Tile()
        tile.ID = tile_elt.find("TILE_IDENTIFIER").text
        tile.SRS = tile_elt.find("HORIZONTAL_CS_CODE").text
        tile.UL[0] = int(tile_elt.find("ULX").text)
        tile.UL[1] = int(tile_elt.find("ULY").text)
        tile_bb = tile_elt.find("B_BOX").text
        tile.BB = tile_bb.split(" ")

        # TODO: Manage properly the case where the polygon cut the dateline (long +/-180�)
        #       take a look to the FixPolygonCoordinatesAtDateLine method into
        #       gdal/ogr/ogrgeometryfactory.cpp
        if (abs(float(tile.BB[1]) - float(tile.BB[3])) > 355.0) or (
            abs(float(tile.BB[5]) - float(tile.BB[7])) > 355.0
        ):
            tile_dateline += 1
            continue

        # Create the polygon
        tile.create_poly_bb()

        # Intersect with the AOI
        if tile.polyBB.Intersects(feature_aoi.GetGeometryRef()):

            for tile_elt_size in tile_elt.findall("./TILE_SIZE_LIST/TILE_SIZE"):
                tile.NRows.append(int(tile_elt_size.find("NROWS").text))
                tile.NCols.append(int(tile_elt_size.find("NCOLS").text))

            tile.create_poly_tile()
            tile_list.append(tile)

    LOGGER.warning(
        "WARNING: some of tiles are excluded due to the dateline issue {}.".format(
            tile_dateline
        )
    )
    return tile_list


def create_tiles_list_L8(filename_tiles_list: str, filename_aoi: str) -> Optional[List[L8Tile]]:
    """Create the L8 tile list according to an aoi

    :param filename_tiles_list: Path to the wrs2_descending folder
    :type filename_tiles_list: string
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: String
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Open the tile list file
    dataSource_tile_list = driver.Open(filename_tiles_list, 0)
    # Check to see if shapefile is found.
    if dataSource_tile_list is None:
        LOGGER.error("ERROR: Could not open {}".format(filename_tiles_list))
        raise IOError

    layer_tile_list = dataSource_tile_list.GetLayer()
    featureCount = layer_tile_list.GetFeatureCount()
    LOGGER.info(
        "Number of features in {}: {}".format(
            pathlib.Path(filename_tiles_list).name, featureCount
        )
    )

    # Open the AOI file
    dataSource_aoi = driver.Open(filename_aoi, 0)
    # Check to see if shapefile is found.
    if dataSource_aoi is None:
        LOGGER.error("ERROR: Could not open {}".format(filename_aoi))
        raise IOError

    layer_aoi = dataSource_aoi.GetLayer()
    featureCount = layer_aoi.GetFeatureCount()
    if featureCount != 1:
        LOGGER.error(
            "ERROR: Number of features in {}: {}".format(
                pathlib.Path(filename_aoi).name, featureCount
            )
        )
        return AssertionError

    # Get the first feature
    feature_aoi = layer_aoi.GetNextFeature()

    tile_list = []

    layer_tile_list.SetSpatialFilter(feature_aoi.GetGeometryRef())

    for feature_tile_list in layer_tile_list:
        tile = L8Tile()

        tile.ID = feature_tile_list.GetField("PR")
        tile.polyBB = feature_tile_list.GetGeometryRef().Clone()

        tile_list.append(tile)

    return tile_list


def get_tile(tile_list: Union[List[S2Tile], List[L8Tile]], tile_id: int) -> \
        Optional[Union[S2Tile, L8Tile]]:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list


    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    """
    if len(tile_list) == 0:
        raise KeyError

    i = -1
    while tile_list[i + 1].ID != tile_id:
        i += 1

    if i != len(tile_list):
        return tile_list[i]
    else:
        raise KeyError


def read_tile_list_from_file(filename_tiles: str) \
        -> Optional[Union[List[S2Tile], List[L8Tile], List[
            EOTile]]]:
    """Returns a tile list from a file previously created

    :param filename_tiles: File containing the tile list (shp file)
    :return: A tile list
    """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Open the tile list file
    dataSource_tile_list = driver.Open(filename_tiles, 0)
    # Check to see if shapefile is found.
    if dataSource_tile_list is None:
        LOGGER.error("ERROR: Could not open {}".format(filename_tiles))
        raise IOError

    layer_tile_list = dataSource_tile_list.GetLayer()
    featureCount = layer_tile_list.GetFeatureCount()
    LOGGER.info(
        "Number of features in {}: {}".format(
            pathlib.Path(filename_tiles).name, featureCount
        )
    )

    tile_list = []
    for feature_tile_list in layer_tile_list:
        tile = EOTile()
        tile.ID = feature_tile_list.GetField("TileID")
        tile.polyBB = feature_tile_list.GetGeometryRef().Clone()
        tile_list.append(tile)

    return tile_list
