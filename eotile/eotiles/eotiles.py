# -*- coding: utf-8 -*-
"""
tile list utilities

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from pathlib import Path
from typing import Optional, Union, List

from lxml import etree as et
import fiona
import geopandas as gp
import pyproj
import shapely
from shapely.geometry import Polygon

from eotile.eotile.eotile import EOTile, L8Tile, S2Tile

# mypy imports


LOGGER = logging.getLogger("dev_logger")


def write_tiles_bb(
    tile_list: Union[List[S2Tile], List[L8Tile]], filename: Path
) -> None:
    """Writes the input tiles to a file

    :param tile_list: The list of input tiles to write
    :type tile_list: list
    :param filename: Path to the output file aux data (Must be a shp file)
    :type filename: Path
    """
    tile_list_tmp = []
    for tile in tile_list:
        tile_list_tmp.append({"geometry": tile.polyBB, "id": tile.ID})
    tiles = gp.GeoDataFrame(tile_list_tmp)

    tiles.to_file(str(filename))


def load_aoi(filename_aoi: Path) -> shapely.geometry.Polygon:
    with fiona.open(filename_aoi) as src:
        p = src.get(0)
    return Polygon(p["geometry"]["coordinates"][0])


def create_tiles_list_s2(filename_tiles_list: Path, filename_aoi: Path) -> List[S2Tile]:
    """Create the S2 tile list according to an aoi file

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: Path
    :return: list of S2 tiles
    :rtype: list
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_s2_from_geometry(filename_tiles_list, geom)


def create_tiles_list_s2_from_geometry(
    filename_tiles_list: Path, aoi: Polygon
) -> List[S2Tile]:
    """Create the S2 tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param aoi: AOI geometry
    :type aoi: shapely.geometry.Polygon
    :return: list of S2 Tiles
    :rtype: list
    """
    # Open the tiles list file
    tree = et.parse(str(filename_tiles_list))
    root = tree.getroot()
    tile_list = []
    for tile_elt in root.findall("./DATA/REPRESENTATION_CODE_LIST/TILE_LIST/TILE"):
        tile = S2Tile()
        tile_bb = tile_elt.find("B_BOX").text
        tile.BB = tile_bb.split(" ")

        # Create the polygon
        # If it crosses the datetime line, then send it to the appropriate function
        if (abs(float(tile.BB[1]) - float(tile.BB[3])) > 355.0) or (
            abs(float(tile.BB[5]) - float(tile.BB[7])) > 355.0
        ):
            tile.datetime_cutter()
        else:  # Otherwise, send to the the standard one
            tile.create_poly_bb()
        # Intersect with the AOI :
        if aoi.intersects(tile.polyBB):
            tile.ID = tile_elt.find("TILE_IDENTIFIER").text
            tile.SRS = tile_elt.find("HORIZONTAL_CS_CODE").text
            tile.UL[0] = int(tile_elt.find("ULX").text)
            tile.UL[1] = int(tile_elt.find("ULY").text)
            for tile_elt_size in tile_elt.findall("./TILE_SIZE_LIST/TILE_SIZE"):
                tile.NRows.append(int(tile_elt_size.find("NROWS").text))
                tile.NCols.append(int(tile_elt_size.find("NCOLS").text))
            tile_list.append(tile)
    return tile_list


def create_tiles_list_l8_from_geometry(
    filename_tiles_list: Path, geom: Polygon
) -> List[L8Tile]:
    """Create the L8 tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param geom: AOI geometry
    :type geom: shapely.geometry.Polygon
    :raises OSError: when the file cannot be open
    :return: list of L8 tiles
    :rtype: list
    """

    # Open the tile list file
    data_source_tile_list = gp.read_file(filename_tiles_list, bbox=geom)
    # Check to see if shapefile is found.
    if data_source_tile_list is None:
        LOGGER.error("ERROR: Could not open %s",filename_tiles_list)
        raise IOError

    feature_count = len(data_source_tile_list)
    LOGGER.info(
        "Number of features in %s: %s",filename_tiles_list.name, feature_count)
    tile_list = []

    # This is still required for fitter filtering
    data_source_filtered = data_source_tile_list[
        data_source_tile_list["geometry"].intersects(geom)
    ][["PR", "geometry"]]
    for __unused, feature_tile_list in data_source_filtered.iterrows():
        tile = L8Tile()
        tile.ID = feature_tile_list["PR"]
        tile.polyBB = feature_tile_list["geometry"]
        tile_list.append(tile)

    return tile_list


def create_tiles_list_l8(filename_tiles_list: Path, filename_aoi: Path) -> List[L8Tile]:
    """Create the L8 tile list according to an aoi

    :param filename_tiles_list: Path to the wrs2_descending folder
    :type filename_tiles_list: pathlib.Path
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: pathlib.Path
    :return: list of L8 tiles
    :rtype: list
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_l8_from_geometry(filename_tiles_list, geom)


def get_tile_l8(tile_list: List[L8Tile], tile_id: int) -> L8Tile:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: L8 tile
    :rtype: L8Tile
    :raises KeyError: when the tile id is not available
    """
    for elt in tile_list:
        if elt.ID == tile_id:
            return elt
    raise KeyError


def get_tile_s2(tile_list: List[S2Tile], tile_id: str) -> S2Tile:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: S2 tile
    :rtype: S2Tile
    :raises KeyError: when the tile id is not available
    """
    for elt in tile_list:
        if elt.ID == tile_id:
            return elt
    raise KeyError


def read_tile_list_from_file(
    filename_tiles: Path,
) -> Union[List[S2Tile], List[L8Tile], List[EOTile]]:
    """Returns a tile list from a file previously created

    :param filename_tiles: File containing the tile list (shp file)
    :return: A tile list
    :raises IOError: when the file cannot be open
    """
    # Open the tile list file
    data_source_tile_list = gp.read_file(filename_tiles)
    # Check to see if shapefile is found.
    if data_source_tile_list is None:
        LOGGER.error("ERROR: Could not open %s",filename_tiles)
        raise IOError

    feature_count = len(data_source_tile_list)
    LOGGER.info(
        "Number of features in %s: %s",filename_tiles.name, feature_count)

    tile_list = []
    for __unused, feature_tile_list in data_source_tile_list[
        ["TileID", "geometry"]
    ].iterrows():
        tile = EOTile()
        tile.ID = feature_tile_list["TileID"]
        tile.polyBB = feature_tile_list["geometry"]
        tile_list.append(tile)
    return tile_list


def bbox_to_wkt(bbox_list) -> str:
    """
    Transforms a bounding box to a wkt polygon
    :param list bbox_list: The bbox list, either it is in str format or list format
    :return: a wkt polygon in str format
    """
    if isinstance(bbox_list, str):
        bbox_list = bbox_list.replace("[", "")
        bbox_list = bbox_list.replace("]", "")
        bbox_list = bbox_list.replace("'", "")
        bbox_list = list(bbox_list.split(","))
    [ul_lat, lr_lat, ul_long, lr_long] = [float(elt) for elt in bbox_list]
    return f"POLYGON (({ul_long} {ul_lat}, {lr_long} {ul_lat}, {lr_long} {lr_lat},\
     {ul_long} {lr_lat}, {ul_long} {ul_lat} ))"


def geom_to_s2_tiles(
    wkt: str, epsg: Optional[str], filename_tiles_s2: Path
) -> List[S2Tile]:
    """
    Generates a s2 tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_s2: The filename to find the tiles in
    :return: list of S2 Tiles
    :rtype: List[S2Tile]
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_s2_from_geometry(filename_tiles_s2, geom)


def geom_to_l8_tiles(
    wkt: str, epsg: Optional[str], filename_tiles_l8: Path
) -> List[L8Tile]:
    """
    Generates a l8 tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_l8: The filename to find the tiles in
    :return: list of L8 Tiles
    :rtype: List[L8Tile]
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_l8_from_geometry(filename_tiles_l8, geom)


def load_wkt_geom(wkt: str, epsg: Optional[str]) -> Polygon:
    """
    Loads a wkt geometry to a shapely objects and reprojects it if needed
    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :return: a shapely Polygon geometry
    """
    geom = shapely.wkt.loads(wkt)
    if epsg is not None:
        source = pyproj.CRS("EPSG:32618")
        target = pyproj.CRS("EPSG:4326")
        project = pyproj.Transformer.from_crs(source, target, always_xy=True).transform
        geom = shapely.ops.transform(project, geom)
    return geom
