# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS GROUP - France.
#
# This file is part of EOTile.
# See https://github.com/CS-SI/eotile for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
tile list utilities

:author: msavinaud; mgerma
:organization: CS GROUP - France
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from pathlib import Path
from typing import Optional, Union
import warnings

import geopandas as gp
import pyproj
import shapely
from shapely.geometry import Polygon


LOGGER = logging.getLogger("dev_logger")


def write_tiles_bb(tile_list: gp.geodataframe.GeoDataFrame, filename: Path, source="Unknown") \
        -> None:
    """Writes the input tiles to a file

    :param tile_list: The list of input tiles to write
    :type tile_list: gp.geodataframe.GeoDataFrame
    :param filename: Path to the output file aux data (Must be a shp file)
    :type filename: Path
    :param source: Source type of the geoDataframe to write
    :type source: String
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
        tiles.to_file(str(filename), layer=source, driver="GPKG")
    else:
        LOGGER.error(f"Unrecognized suffix {filename.suffix}")


def load_aoi(filename_aoi: Path) -> shapely.geometry.Polygon:
    """
    Loads an Area of Interest from a file using geopandas
    :param filename_aoi: The path to the file containing the AOI
    :type filename_aoi: Path
    :return: the geometry polygon
    :rtype: shapely.geometry.Polygon
    """
    aoi = gp.read_file(filename_aoi)
    aoi = aoi.to_crs("epsg:4326")
    geometry = aoi.iloc[0].geometry
    if len(aoi) > 1:
        LOGGER.warning(f"The input file {filename_aoi} contains more than one geometry")
    return geometry


def get_tile(tile_list: gp.geodataframe.GeoDataFrame, tile_id: str) -> gp.geoseries:
    """Returns a tile from a tile list from its tile ID
    raises KeyError if the ID corresponds to no tile within the list

    :param tile_list: The list of tiles to look in
    :param tile_id: The tile id of the tile to output
    :return: EO tile
    :rtype: EOTile
    :raises KeyError: when the tile id is not available
    """
    try:
        tiles_df = tile_list.set_index("id")
        tile = tiles_df.loc[tile_id]
        tile["id"] = tile_id
    except KeyError:
        LOGGER.error("Tile ID is not valid. Exiting...")
        raise SystemExit(f'Invalid Tile id {tile_id}')

    return tile


def parse_to_list(input_elt: Union[str, list]) -> list:
    """
    Transforms an input string to a list

    :param list input_elt: The input element, either it is in str format or list format
    :return: a list
    """
    if isinstance(input_elt, str):
        input_elt = input_elt.replace("[", "")
        input_elt = input_elt.replace("]", "")
        input_elt = input_elt.replace("'", "")
        input_elt = input_elt.replace(" ", "")
        parsing_dict = {}
        for parsing_separator in [",", "\n"]:
            parsing_dict[len(list(input_elt.split(parsing_separator)))] = \
                list(input_elt.split(parsing_separator))
        return parsing_dict[max(parsing_dict.keys())]
    return input_elt


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
    try:
        [ul_lat, lr_lat, ul_long, lr_long] = [float(elt) for elt in bbox_list]
    except ValueError as error:
        LOGGER.error(error)
        LOGGER.error("Input was recognized as a BBOX but values are incorrect")
        raise ValueError
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
    wkt: str, epsg: Optional[str], filename_tiles_eo: Path, min_overlap=None
) -> gp.geodataframe.GeoDataFrame:
    """
    Generates a eo tile list from a wkt string

    :param wkt: A wkt polygon in str format
    :param epsg: An optional in the epsg code in case it is not WGS84
    :param filename_tiles_eo: The filename to find the tiles in
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of EO Tiles
    :rtype: gp.geodataframe.GeoDataFrame
    """
    geom = load_wkt_geom(wkt, epsg)
    return create_tiles_list_eo_from_geometry(filename_tiles_eo, geom, min_overlap)


def create_tiles_list_eo_from_geometry(
    filename_tiles_list: Path, geom: Polygon, min_overlap=None
) -> gp.geodataframe.GeoDataFrame:
    """Create the EO tile list according to an aoi geometry

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: str
    :param geom: AOI geometry
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :type geom: shapely.geometry.Polygon
    :raises OSError: when the file cannot be open
    :return: list of EO tiles
    :rtype: gp.geodataframe.GeoDataFrame
    """

    # Open the tile list file
    data_source_filtered = gp.read_file(filename_tiles_list, mask=geom)
    # Check to see if shapefile is found.
    if data_source_filtered is None:
        LOGGER.error("ERROR: Could not open %s", filename_tiles_list)
        raise IOError

    feature_count = len(data_source_filtered)
    LOGGER.info("Number of features in %s: %s", filename_tiles_list.name, feature_count)
    warnings.filterwarnings("ignore")
    # Ignore the
    # UserWarning: Geometry is in a geographic CRS.
    # Results from 'area' are likely incorrect.
    # Use 'GeoSeries.to_crs()' to re-project geometries to a projected CRS before this operation.
    #
    # We keep the square degrees results as is. Since we use a ratio, this does not matter
    if min_overlap is not None:
        data_source_filtered = data_source_filtered[
            data_source_filtered.intersection(geom).area / data_source_filtered.area
            >= float(min_overlap)
        ]

    return data_source_filtered


def load_tiles_list_eo(
    filename_tiles_list: Path
) -> gp.geodataframe.GeoDataFrame:
    """Create the EO tile list according to an aoi in ogr geometry format

    :param filename_tiles_list: Path to the XML file containing the list of tiles
    :type filename_tiles_list: Path
    :raises OSError: when the file cannot be open
    :return: list of EO tiles
    :rtype: gp.geodataframe.GeoDataFrame
    """

    # Open the tile list file
    data_source_filtered = gp.read_file(filename_tiles_list)
    # Check to see if shapefile is found.
    if data_source_filtered is None:
        LOGGER.error("ERROR: Could not open %s", filename_tiles_list)
        raise IOError

    feature_count = len(data_source_filtered)
    LOGGER.info("Number of features in %s: %s", filename_tiles_list.name, feature_count)

    return data_source_filtered


def create_tiles_list_eo(
    filename_tiles_list: Path, filename_aoi: Path, min_overlap=None
) -> gp.geodataframe.GeoDataFrame:
    """Create the EO tile list according to an aoi

    :param filename_tiles_list: Path to the wrs2_descending folder
    :type filename_tiles_list: pathlib.Path
    :param filename_aoi: Path to the input AOI file (Must be a shp file)
    :type filename_aoi: pathlib.Path
    :param min_overlap: (Optional, default=None) Minimum percentage of overlap
    :return: list of EO tiles
    :rtype: gp.geodataframe.GeoDataFrame
    """
    # Load the aoi
    geom = load_aoi(filename_aoi)
    return create_tiles_list_eo_from_geometry(filename_tiles_list, geom, min_overlap)
