# -*- coding: utf-8 -*-
"""
tile list utilities

:author: msavinaud; mgerma
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
from shapely.geometry import Polygon, MultiPolygon

from eotile.eotile.eotile import EOTile, S2Tile

LOGGER = logging.getLogger("dev_logger")


def write_tiles_bb(tile_list: Union[List[S2Tile], List[EOTile]], filename: Path) -> None:
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
    tiles = tiles.set_crs(epsg=4326)
    if filename.suffix == ".shp":
        # Shapefile case
        tiles.to_file(str(filename))
    elif filename.suffix == ".geojson":
        # GeoJSON case
        tiles.to_file(str(filename), driver="GeoJSON")
    elif filename.suffix == ".gpkg":
        # GeoJSON case
        tiles.to_file(str(filename), layer=tile_list[0].source, driver="GPKG")
    else:
        LOGGER.error(f"Unrecognized suffix {filename.suffix}")


def load_aoi(filename_aoi: Path) -> shapely.geometry.Polygon:
    with fiona.open(filename_aoi) as src:
        p = src.get(0)
    if p["geometry"]["type"] == "Polygon":
        geometry = Polygon(p["geometry"]["coordinates"][0])
    elif p["geometry"]["type"] == "MultiPolygon":
        poly_list = []
        for poly in p["geometry"]["coordinates"]:
            poly_list.append(Polygon(poly[0]))
        geometry = MultiPolygon(poly_list)
    else:
        LOGGER.error(f"file must contain a (multi)polygon, not {p['geometry']['type']}")
    return geometry


def create_tiles_list_s2(
    filename_tiles_list: Path, filename_aoi: Path, min_overlap=None
) -> List[S2Tile]:
    """Create the S2 tile list according to an aoi file

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: Path
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of S2 tiles
    :rtype: list
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_s2_from_geometry(filename_tiles_list, geom, min_overlap)


def create_tiles_list_s2_from_geometry(
    filename_tiles_list: Path, aoi: Polygon, min_overlap=None
) -> List[S2Tile]:
    """Create the S2 tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param aoi: AOI geometry
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
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
            if min_overlap is not None and aoi.intersection(
                tile.polyBB
            ).area / tile.polyBB.area < float(min_overlap):
                continue
            tile.ID = tile_elt.find("TILE_IDENTIFIER").text
            tile.SRS = tile_elt.find("HORIZONTAL_CS_CODE").text
            tile.UL[0] = int(tile_elt.find("ULX").text)
            tile.UL[1] = int(tile_elt.find("ULY").text)
            for tile_elt_size in tile_elt.findall("./TILE_SIZE_LIST/TILE_SIZE"):
                tile.NRows.append(int(tile_elt_size.find("NROWS").text))
                tile.NCols.append(int(tile_elt_size.find("NCOLS").text))
            tile_list.append(tile)
    return tile_list


def get_tile(tile_list: List[EOTile], tile_id: str) -> EOTile:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: EO tile
    :rtype: EOTile
    :raises KeyError: when the tile id is not available
    """
    for elt in tile_list:
        if elt.ID == tile_id:
            return elt
    raise KeyError


def get_tile_s2(tile_list: List[S2Tile], tile_id: str) -> S2Tile:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    Note: This function exists because of mypy
    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: EO tile
    :rtype: EOTile
    :raises KeyError: when the tile id is not available
    """
    for elt in tile_list:
        if elt.ID == tile_id:
            return elt
    raise KeyError


def read_tile_list_from_file(
    filename_tiles: Path,
) -> Union[List[S2Tile], List[EOTile]]:
    """Returns a tile list from a file previously created

    :param filename_tiles: File containing the tile list (shp file)
    :return: A tile list
    :raises IOError: when the file cannot be open
    """
    # Open the tile list file
    data_source_tile_list = gp.read_file(filename_tiles)
    # Check to see if shapefile is found.
    if data_source_tile_list is None:
        LOGGER.error("ERROR: Could not open %s", filename_tiles)
        raise IOError

    feature_count = len(data_source_tile_list)
    LOGGER.info("Number of features in %s: %s", filename_tiles.name, feature_count)

    tile_list = []
    for __unused, feature_tile_list in data_source_tile_list[["TileID", "geometry"]].iterrows():
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
    LOGGER.warning("bbox_to_wkt is a depreciated function, shouldn't be used !")
    if isinstance(bbox_list, str):
        bbox_list = bbox_list.replace("[", "")
        bbox_list = bbox_list.replace("]", "")
        bbox_list = bbox_list.replace("'", "")
        bbox_list = list(bbox_list.split(","))
    [ul_lat, lr_lat, ul_long, lr_long] = [float(elt) for elt in bbox_list]
    return f"POLYGON (({ul_long} {ul_lat}, {lr_long} {ul_lat}, {lr_long} {lr_lat},\
     {ul_long} {lr_lat}, {ul_long} {ul_lat} ))"

def bbox_to_list(bbox_list) -> list:
    """
    Transforms a bounding box str from args to a list

    :param list bbox_list: The bbox list, either it is in str format or list format
    :return: a list for the four coordinates
    """
    if isinstance(bbox_list, str):
        bbox_list = bbox_list.replace("[", "")
        bbox_list = bbox_list.replace("]", "")
        bbox_list = bbox_list.replace("'", "")
        bbox_list = list(bbox_list.split(","))
    [ul_lat, lr_lat, ul_long, lr_long] = [float(elt) for elt in bbox_list]
    return [ul_lat, lr_lat, ul_long, lr_long]


def geom_to_s2_tiles(
    wkt: str, epsg: Optional[str], filename_tiles_s2: Path, min_overlap=None
) -> List[S2Tile]:
    """
    Generates a s2 tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_s2: The filename to find the tiles in
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of S2 Tiles
    :rtype: List[S2Tile]
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_s2_from_geometry(filename_tiles_s2, geom, min_overlap)


def load_wkt_geom(wkt: str, epsg: Optional[str]) -> Polygon:
    """
    Loads a wkt geometry to a shapely objects and reprojects it if needed
    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :return: a shapely Polygon geometry
    """
    geom = shapely.wkt.loads(wkt)
    if epsg is not None:
        source = pyproj.CRS(f"EPSG:{epsg}")
        target = pyproj.CRS("EPSG:4326")
        project = pyproj.Transformer.from_crs(source, target, always_xy=True).transform
        geom = shapely.ops.transform(project, geom)
    return geom


def geom_to_eo_tiles(
    wkt: str, epsg: Optional[str], filename_tiles_eo: Path, tile_type, min_overlap=None
) -> List[EOTile]:
    """
    Generates a eo tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_eo: The filename to find the tiles in
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of EO Tiles
    :rtype: List[EOTile]
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_eo_from_geometry(filename_tiles_eo, geom, tile_type, min_overlap)


def create_tiles_list_eo_from_geometry(
    filename_tiles_list: Path, geom: Polygon, tile_type, min_overlap=None
) -> List[EOTile]:
    """Create the EO tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param geom: AOI geometry
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :type geom: shapely.geometry.Polygon
    :raises OSError: when the file cannot be open
    :return: list of EO tiles
    :rtype: list
    """

    # Open the tile list file
    data_source_filtered = gp.read_file(filename_tiles_list, mask=geom)
    # Check to see if shapefile is found.
    if data_source_filtered is None:
        LOGGER.error("ERROR: Could not open %s", filename_tiles_list)
        raise IOError

    feature_count = len(data_source_filtered)
    LOGGER.info("Number of features in %s: %s", filename_tiles_list.name, feature_count)
    tile_list = []
    if min_overlap is not None:
        data_source_filtered = data_source_filtered[
            data_source_filtered.intersection(geom).area / data_source_filtered.area
            >= float(min_overlap)
        ]
    for __unused, feature_tile_list in data_source_filtered.iterrows():
        tile = EOTile()
        if tile_type == "L8":
            tile.ID = str(feature_tile_list["PR"])
        elif tile_type == "Copernicus":
            id_elt = feature_tile_list["id"]
            id_elt = id_elt.split("_")
            if len(id_elt) == 9:
                tile.ID = "".join([id_elt[i] for i in [4, 6]])
            elif len(id_elt) == 1:
                tile.ID = id_elt[0]
            else:
                LOGGER.error(f"Unrecognized id element : {id_elt}")
        else:
            tile.ID = feature_tile_list["id"]
        tile.polyBB = feature_tile_list["geometry"]
        tile.source = tile_type
        tile_list.append(tile)

    return tile_list


def create_tiles_list_eo(
    filename_tiles_list: Path, filename_aoi: Path, tile_type, min_overlap=None
) -> List[EOTile]:
    """Create the EO tile list according to an aoi

    :param filename_tiles_list: Path to the wrs2_descending folder
    :type filename_tiles_list: pathlib.Path
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: pathlib.Path
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of EO tiles
    :rtype: list
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_eo_from_geometry(filename_tiles_list, geom, tile_type, min_overlap)
