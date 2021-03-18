# -*- coding: utf-8 -*-
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
    geom_to_eo_tiles,
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

    if bbox_reg.match(input_value) and bbox_reg.match(input_value).string == input_value:
        return "bbox"

    if tile_id_reg.match(input_value) and tile_id_reg.match(input_value).string == input_value:
        return "tile_id"

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
    # Creating DEV logger
    dev_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    dev_handler = logging.FileHandler("dev_log.log")
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
    """
    if induced_type == "wkt":
        wkt = input_arg
        tile_list = geom_to_eo_tiles(wkt, epsg, filename_tiles, tile_type, min_overlap)
    elif induced_type == "location":
        geom = build_nominatim_request(location_type, input_arg, threshold)
        tile_list = create_tiles_list_eo_from_geometry(filename_tiles, geom, tile_type, min_overlap)
    elif induced_type == "bbox":
        bbox = bbox_to_list(input_arg)
        geom = box(*bbox)
        tile_list = create_tiles_list_eo_from_geometry(filename_tiles, geom, tile_type, min_overlap)
    elif induced_type == "file":
        aoi_filepath = Path(input_arg)
        tile_list = create_tiles_list_eo(filename_tiles, aoi_filepath, tile_type, min_overlap)
        dev_logger.info("Nb of %s tiles which crossing the AOI: %s", tile_type, len(tile_list))
    else:
        dev_logger.error("Unrecognized Option: %s", induced_type)
        tile_list = []

    return tile_list


def build_nominatim_request(location_type, input_arg, threshold):
    """
    Builds an http requests for nominatim, then runs it and outputs a geometry object
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
    s2_only=False,
    l8_only=False,
    srtm=False,
    cop=False,
    location_type=None,
    min_overlap=None,
    epsg=None,
    threshold=None,
    verbose=None,
):
    """
    Main module of eotile
    Outputs a list of four lists containing tiles from respectively : Sentinel-2,
    Landscape 8, SRTM DEM and Copernicus

    :param input_arg:  Choose amongst : a file, a tile_id, a location, a wkt, a bbox
    :type input_arg: Str
    :param logger_file: [Optional, default = None] Redirect information from standard output to a file
    given by its path
    :type logger_file: Str
    :param epsg: [Optional, default = "4326"] Specify the epsg of the input
    :type epsg: Str
    :param min_overlap: [Optional, default = None] Minimum percentage of overlap to
    consider a tile (0 to 1)
    :type min_overlap: Str
    :param threshold: [Optional, default = None] For large polygons at high resolution,
    you might want to simplify them using a threshold (0 to 1)
    :type min_overlap: Str
    :param s2_only: [Optional, default = None] Do you want to ignore l8 tiles ?
    :type s2_only: Boolean
    :param l8_only: [Optional, default = None] Do you want to ignore s2 tiles ?
    :type l8_only: Boolean
    :param srtm: [Optional, default = None] Do you want to use SRTM tiles ?
    :type srtm: Boolean
    :param cop: [Optional, default = None] Do you want to use Copernicus tiles ?
    :type cop: Boolean
    :param location_type: [Optional, default = None] Specify the value of the location
    (city, county, state, country)
    :type location_type: Str
    :param verbose: [Optional, default = None] Verbosity value, from 1 to 2
    :type verbose: Integer
    """
    if verbose is None:  # Default
        log_level = logging.WARNING
    elif verbose == 1:
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
            input_arg,
            aux_data_dirpath,
            s2_only,
            l8_only,
            srtm,
            cop,
            min_overlap,
        )

    else:
        if not l8_only:
            # S2 Tiles
            filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"
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

        if not s2_only:
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
