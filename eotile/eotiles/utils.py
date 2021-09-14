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
EO tile

:author: mgerma
:organization: CS GROUP - France
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import re
from pathlib import Path

import requests
from geopy.geocoders import Nominatim
from shapely.geometry import box, shape

from eotile.eotiles.eotiles import (
    bbox_to_list,
    create_tiles_list_eo,
    create_tiles_list_eo_from_geometry,
    geom_to_eo_tiles, parse_to_list
)


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

    tile_id_pattern = "(([0-9]){4,6}|([0-9]){2}([A-Z]){3}|(N|S)([0-9]){2}(E|W)([0-9]){3}|srtm_([0-9]){2}_([0-9]){2})"
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
    
