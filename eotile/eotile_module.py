# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS Group.
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
EO tile

:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import re
from pathlib import Path

import pkg_resources
import requests
from geopy.geocoders import Nominatim
from shapely.geometry import box, shape

from eotile.eotiles.eotiles import (
    bbox_to_list,
    create_tiles_list_eo,
    create_tiles_list_eo_from_geometry,
    geom_to_eo_tiles, parse_to_list
)
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id


# noinspection Mypy
def input_matcher(input_value: str) -> str:
    """
    Induces the type of the input from the user input

    :param input_value: input provided by user of the cli
    :return: type of the input: wkt, bbox, tile_id, file, location
    :rtype: str
    :raises ValueError: when the input value cannot be parsed
    """
    poly_pattern = "(POLYGON|Polygon|MULTIPOLYGON|Multipolygon)(.*?)"

    bbox_pattern = "(.*?)(([0-9]|.|-|,|'| )*,).(.*?)"

    tile_id_pattern = "(([0-9]){4,6}|([0-9]){2}([A-Z]){3}|(N|S)([0-9]){2}(E|W)([0-9]){3})"

    poly_reg = re.compile(poly_pattern)
    bbox_reg = re.compile(bbox_pattern)
    tile_id_reg = re.compile(tile_id_pattern)

    if poly_reg.match(input_value) and poly_reg.match(input_value).string == input_value:
        return "wkt"

    # To parse a tile_id (list), we check that all inputted values corresponds to the tile_id regex
    list_input = parse_to_list(input_value)
    can_be_tile_id = True
    for possible_tile in list_input:
        if not(tile_id_reg.match(possible_tile) and
               tile_id_reg.match(possible_tile).string == possible_tile):
            can_be_tile_id = False
    if can_be_tile_id:
        return "tile_id"

    if bbox_reg.match(input_value) and bbox_reg.match(input_value).string == input_value:
        return "bbox"

    if Path(input_value).exists():
        return "file"

    geolocator = Nominatim(user_agent="eotile")
    location = geolocator.geocode(input_value)
    if location is not None:
        location_type = location.raw["type"]
        if location_type == "administrative":
            return "location"
        raise ValueError(
            "This location is has no administrative border: "
            + f"{input_value}, type= {location_type}"
        )

    raise ValueError(f"Cannot parse this input: {input_value}")


def build_logger(level, user_file_name=None):
    """
    Builds two loggers : a dev one as well as a user one.
    :param level: The desired level of logging for the dev log.
    If is logging.ERROR (default) then the logging is handled on the stream.
    Otherwise, it outputs in the dev_log.log file
    :type level: logging level
    :returns: The two logger objects
    """
    # Creating DEV logger
    dev_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    if level != logging.ERROR:
        dev_handler = logging.FileHandler("dev_log.log")
    else:
        dev_handler = logging.StreamHandler()
    dev_handler.setFormatter(dev_formatter)

    dev_logger = logging.getLogger("dev_logger")
    dev_logger.setLevel(level)
    dev_logger.addHandler(dev_handler)

    # Creating User logger
    user_formatter = logging.Formatter("%(message)s")

    if user_file_name is not None:
        user_handler = logging.FileHandler(user_file_name)
    else:
        user_handler = logging.StreamHandler()
    user_handler.setFormatter(user_formatter)

    user_logger = logging.getLogger("user_logger")
    user_logger.setLevel(logging.INFO)
    user_logger.addHandler(user_handler)

    return dev_logger, user_logger


def treat_eotiles(
    induced_type,
    input_arg,
    tile_type,
    dev_logger,
    epsg,
    filename_tiles,
    min_overlap,
    location_type,
    threshold,
):
    """
    Treats Tiles that can be loaded from a standard geography file
    :param induced_type: Induced type of the input argument
    :type induced_type: string
    :param input_arg: Argument out of which we select the tiles.
    :type input_arg: Union(list, str)
    :param tile_type: type of tiles (what satellite do they come from)
    :type tile_type: str
    :param dev_logger: the dev logger to log dev info to
    :type dev_logger: logging object
    :param epsg: if input is a wkt polygon not coded in epsg 4326 (wgs84), then a conversion from
    that epsg is produced
    :type epsg: str
    :param filename_tiles: File to get the tiles from
    :type filename_tiles: Path
    :param min_overlap: minimum overlap value for a tile to be considered matching with
    the geometry specified in input.
    :type min_overlap: str
    :param location_type: specified type of nominatim request
    :type location_type: str
    :param threshold: simplifying factor for the nominatim request
    :type threshold: str
    """
    if induced_type == "wkt":
        wkt = input_arg
        tile_list = geom_to_eo_tiles(wkt, epsg, filename_tiles, min_overlap)
    elif induced_type == "location":
        geom = build_nominatim_request(location_type, input_arg, threshold)
        tile_list = create_tiles_list_eo_from_geometry(filename_tiles, geom, min_overlap)
    elif induced_type == "bbox":
        bbox = bbox_to_list(input_arg)
        geom = box(*bbox)
        tile_list = create_tiles_list_eo_from_geometry(filename_tiles, geom, min_overlap)
    elif induced_type == "file":
        aoi_filepath = Path(input_arg)
        tile_list = create_tiles_list_eo(filename_tiles, aoi_filepath, min_overlap)
        dev_logger.info("Nb of %s tiles which crossing the AOI: %s", tile_type, len(tile_list))
    else:
        dev_logger.error("Unrecognized Option: %s", induced_type)
        tile_list = []

    return tile_list


def build_nominatim_request(location_type, input_arg, threshold):
    """
    Builds an http requests for nominatim, then runs it and outputs a geometry object
    :param input_arg: Argument out of which we select the tiles.
    :type input_arg: Union(list, str)
    :param location_type: specified type of nominatim request
    :type location_type: str
    :param threshold: simplifying factor for the nominatim request
    :type threshold: str
    """
    if location_type is not None:
        req = location_type
    else:
        req = "q"
    url = (
        f"https://nominatim.openstreetmap.org/search?{req}={input_arg}"
        f"&format=geojson&polygon_geojson=1&limit=1"
    )
    if threshold is not None:
        url += f"& polygon_threshold = {threshold}"
    data = requests.get(url)
    elt = data.json()
    geom = shape(elt["features"][0]["geometry"])
    return geom


def main(
    input_arg,
    logger_file=None,
    no_l8=False,
    no_s2=False,
    srtm=False,
    cop=False,
    location_type=None,
    min_overlap=None,
    epsg=None,
    threshold=None,
    verbose=None,
    overlap=False,
):
    """
    Main module of eotile
    Outputs a list of four lists containing tiles from respectively : Sentinel-2,
    Landscape 8, SRTM DEM and Copernicus

    :param input_arg:  Choose amongst : a file, a tile_id, a location, a wkt, a bbox
    :type input_arg: Str
    :param logger_file: [Optional, default = None] Redirect information
    from standard output to a file given by its path
    :type logger_file: Str
    :param epsg: [Optional, default = "4326"] Specify the epsg of the input
    :type epsg: Str
    :param min_overlap: [Optional, default = None] Minimum percentage of overlap to
    consider a tile (0 to 1)
    :type min_overlap: Str
    :param threshold: [Optional, default = None] For large polygons at high resolution,
    you might want to simplify them using a threshold (0 to 1)
    :type min_overlap: Str
    :param no_l8: [Optional, default = None] Do you want to ignore l8 tiles ?
    :type no_l8: Boolean
    :param no_s2: [Optional, default = None] Do you want to ignore s2 tiles ?
    :type no_s2: Boolean
    :param srtm: [Optional, default = None] Do you want to use SRTM tiles ?
    :type srtm: Boolean
    :param cop: [Optional, default = None] Do you want to use Copernicus tiles ?
    :type cop: Boolean
    :param location_type: [Optional, default = None] Specify the value of the location
    (city, county, state, country)
    :type location_type: Str
    :param verbose: [Optional, default = None] Verbosity value, from 1 to 2
    :type verbose: Integer
    :param overlap: (Optional, default = False) Do you want to use the overlapping source file ?
    :type overlap: Boolean
    """
    if verbose is None:  # Default, no file
        log_level = logging.ERROR
    elif verbose == 1:  # Else, in a file
        log_level = logging.WARNING
    elif verbose == 2:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    dev_logger, user_logger = build_logger(log_level, logger_file)

    with open(pkg_resources.resource_filename(__name__, "config/data_path")) as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = Path(pkg_resources.resource_filename(__name__, data_path.strip()))
    tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop = [], [], [], []
    induced_type = input_matcher(input_arg)

    if induced_type == "tile_id":
        (tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop) = get_tiles_from_tile_id(
            parse_to_list(input_arg),
            aux_data_dirpath,
            no_l8,
            no_s2,
            srtm,
            cop,
            min_overlap,
            overlap
        )

    else:
        if not no_s2:
            # S2 Tiles
            if not overlap:
                filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"
            else:
                filename_tiles_s2 = aux_data_dirpath / "s2_with_overlap.gpkg"
            tile_list_s2 = treat_eotiles(
                induced_type,
                input_arg,
                "S2",
                dev_logger,
                epsg,
                filename_tiles_s2,
                min_overlap,
                location_type,
                threshold,
            )

        if not no_l8:
            # L8 Tiles
            filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
            tile_list_l8 = treat_eotiles(
                induced_type,
                input_arg,
                "L8",
                dev_logger,
                epsg,
                filename_tiles_l8,
                min_overlap,
                location_type,
                threshold,
            )

        if srtm:
            # SRTM Tiles
            filename_tiles_srtm = aux_data_dirpath / "srtm_tiles.gpkg"
            tile_list_srtm = treat_eotiles(
                induced_type,
                input_arg,
                "SRTM",
                dev_logger,
                epsg,
                filename_tiles_srtm,
                min_overlap,
                location_type,
                threshold,
            )

        if cop:
            # Copernicus Tiles
            filename_tiles_cop = aux_data_dirpath / "cop_tiles.gpkg"
            tile_list_cop = treat_eotiles(
                induced_type,
                input_arg,
                "Copernicus",
                dev_logger,
                epsg,
                filename_tiles_cop,
                min_overlap,
                location_type,
                threshold,
            )
    #
    # Outputting the result
    return [tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop]
