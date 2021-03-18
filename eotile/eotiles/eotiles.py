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
from typing import Optional, List

import fiona
import geopandas as gp
import pyproj
import shapely
from shapely.geometry import Polygon, MultiPolygon

LOGGER = logging.getLogger("dev_logger")


def write_tiles_bb(tile_list: gp.geodataframe, filename: Path) -> None:
    """Writes the input tiles to a file

    :param tile_list: The list of input tiles to write
    :type tile_list: list
    :param filename: Path to the output file aux data (Must be a shp file)
    :type filename: Path
    """
    tiles = tile_list.set_crs(epsg=4326)
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


def get_tile(tile_list: gp.geodataframe, tile_id: str) -> gp.geoseries:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: EO tile
    :rtype: EOTile
    :raises KeyError: when the tile id is not available
    """
    tiles_df = tile_list.set_index("id")
    return tiles_df.loc[tile_id]


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
) -> gp.geodataframe:
    """
    Generates a eo tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_eo: The filename to find the tiles in
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :param tile_type: Type of the tile
    :return: list of EO Tiles
    :rtype: gp.geodataframe
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_eo_from_geometry(filename_tiles_eo, geom, tile_type, min_overlap)


def create_tiles_list_eo_from_geometry(
    filename_tiles_list: Path, geom: Polygon, tile_type, min_overlap=None
) -> gp.geodataframe:
    """Create the EO tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param geom: AOI geometry
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :type geom: shapely.geometry.Polygon
    :param tile_type: Type of the tiles
    :type tile_type: Str
    :raises OSError: when the file cannot be open
    :return: list of EO tiles
    :rtype: list
    """

    # Open the tile list file
    data_source_filtered = gp.read_file(filename_tiles_list, mask=geom, index_col="id")
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

    return data_source_filtered


def load_tiles_list_eo(
    filename_tiles_list: Path
) -> gp.geodataframe:
    """Create the EO tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param tile_type: Type of the tiles
    :type tile_type: Str
    :raises OSError: when the file cannot be open
    :return: list of EO tiles
    :rtype: list
    """

    # Open the tile list file
    data_source_filtered = gp.read_file(filename_tiles_list, index_col="id")
    # Check to see if shapefile is found.
    if data_source_filtered is None:
        LOGGER.error("ERROR: Could not open %s", filename_tiles_list)
        raise IOError

    feature_count = len(data_source_filtered)
    LOGGER.info("Number of features in %s: %s", filename_tiles_list.name, feature_count)

    return data_source_filtered


def create_tiles_list_eo(
    filename_tiles_list: Path, filename_aoi: Path, tile_type, min_overlap=None
) -> gp.geodataframe:
    """Create the EO tile list according to an aoi

    :param filename_tiles_list: Path to the wrs2_descending folder
    :type filename_tiles_list: pathlib.Path
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: pathlib.Path
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :param tile_type: Type of the tile
    :return: list of EO tiles
    :rtype: list
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_eo_from_geometry(filename_tiles_list, geom, tile_type, min_overlap)
