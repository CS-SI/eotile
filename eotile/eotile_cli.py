# -*- coding: utf-8 -*-
"""
EO tile

:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import argparse
import logging
import sys
from pathlib import Path
import re

from geopy.geocoders import Nominatim
import pkg_resources
import requests
from shapely.geometry import shape

from eotile.eotiles.eotiles import (
    bbox_to_wkt,
    create_tiles_list_l8,
    create_tiles_list_s2,
    geom_to_l8_tiles,
    geom_to_s2_tiles,
    write_tiles_bb,
    create_tiles_list_l8_from_geometry,
    create_tiles_list_s2_from_geometry
)
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id


def build_logger(level, user_file_name=None):
    # Creating DEV logger
    dev_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    dev_handler = logging.FileHandler("dev_log.log")
    dev_handler.setFormatter(dev_formatter)

    dev_logger = logging.getLogger("dev_logger")
    dev_logger.setLevel(level)
    dev_logger.addHandler(dev_handler)

    # Creating User logger
    user_formatter = logging.Formatter('%(message)s')

    if user_file_name is not None:
        user_handler = logging.FileHandler(user_file_name)
    else:
        user_handler = logging.StreamHandler()
    user_handler.setFormatter(user_formatter)

    user_logger = logging.getLogger("user_logger")
    user_logger.setLevel(logging.INFO)
    user_logger.addHandler(user_handler)

    return dev_logger, user_logger

def input_matcher(input_value:str)->str:
    """
    Induces the type of the input from the user input

    :param input_value: input provided by user of the cli
    :return: type of the input: wkt, bbox, tile_id, file, location
    :rtype: str
    """
    poly_pattern = "(POLYGON|Polygon|MULTIPOLYGON|Multipolygon)(.*?)"

    bbox_pattern = "(.*?)(([0-9]|.|-|,|'| )*,).(.*?)"

    tile_id_pattern = "(([0-9]){6}|([0-9]){2}([A-Z]){3})"

    poly_reg = re.compile(poly_pattern)
    bbox_reg = re.compile(bbox_pattern)
    tile_id_reg = re.compile(tile_id_pattern)

    if poly_reg.match(input_value) and poly_reg.match(input_value).string == input_value:
        induced_type = "wkt"
    elif bbox_reg.match(input_value) and bbox_reg.match(input_value).string == input_value:
        induced_type = "bbox"
    elif tile_id_reg.match(input_value) and tile_id_reg.match(input_value).string == input_value:
        induced_type = "tile_id"
    elif Path(input_value).exists():
        induced_type = "file"
    else:
        induced_type = "location"
    return induced_type


# Location

def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Choose amongst : file, tile_id, location, wkt, bbox. Then specify the argument"
    )
    parser.add_argument("-epsg", help="Specify the epsg of the input")
    parser.add_argument(
        "-s2_only", action="store_true", help="output S2 tiles which intersect the aoi"
    )
    parser.add_argument(
        "-l8_only", action="store_true", help="output L8 tiles which intersect the aoi"
    )

    # Output arguments

    parser.add_argument("-to_file", help="Write tiles to a file")
    parser.add_argument(
        "-to_wkt",
        action="store_true",
        help="Output the geometry of matching tiles with wkt format on standard output",
    )
    parser.add_argument(
        "-to_bbox",
        action="store_true",
        help="Output the bounding box of matching tiles on standard output",
    )
    parser.add_argument(
        "-to_tile_id",
        action="store_true",
        help="Output the id(s) of matching tiles on standard output",
    )
    parser.add_argument(
        "-to_location",
        action="store_true",
        help="Output the location of the centroid of matching tiles "
        "on standard output",
    )

    parser.add_argument("-v", "--verbosity", action="count",
                        help="Increase output verbosity")

    parser.add_argument("-logger_file",
                        help="Redirect information from standard output to a file")

    parser.add_argument("-location_type",
                        help="If needed, specify the location type that is requested (city, county, state, country)")

    parser.add_argument("-threshold",
                        help="For large polygons at high resolution, you might want to simplify them using a threshold"
                             "(0 to 1)")
    return parser


def main(arguments=None):
    """
    Command line interface to perform

    :param list arguments: list of arguments
    """
    arg_parser = build_parser()
    args = arg_parser.parse_args(args=arguments)
    if args.verbosity is None:  # Default
        log_level = logging.ERROR
    elif args.verbosity == 1:
        log_level = logging.WARNING
    elif args.verbosity == 2:
        log_level = logging.INFO
    elif args.verbosity > 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.NOTSET
    dev_logger, user_logger = build_logger(log_level, args.logger_file)


    with open(pkg_resources.resource_filename(__name__, 'config/data_path')) as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = Path(pkg_resources.resource_filename(__name__, data_path.strip()))
    tile_list_s2, tile_list_l8 = [], []
    induced_type = input_matcher(args.input)

    if induced_type == "tile_id":
        tile_list_s2, tile_list_l8 = get_tiles_from_tile_id(
            args.input, aux_data_dirpath, args.s2_only, args.l8_only
        )

    else:
        if not args.l8_only:
            # S2 Tiles
            filename_tiles_s2 = (
                aux_data_dirpath
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            if induced_type == "wkt":
                wkt = args.input
                tile_list_s2 = geom_to_s2_tiles(wkt, args.epsg, filename_tiles_s2)
            elif induced_type == "location":
                if args.location_type is not None:
                    req = "args.location_type"
                else:
                    req = "q"
                url = f"https://nominatim.openstreetmap.org/search?{req}={args.input}" \
                      f"&format=geojson&polygon_geojson=1&limit=1"
                if args.threshold is not None:
                    url += f'& polygon_threshold = {args.threshold}'
                data = requests.get(url)
                elt = data.json()
                geom = shape(elt["features"][0]["geometry"])
                tile_list_s2 = create_tiles_list_s2_from_geometry(filename_tiles_s2, geom)
            elif induced_type == "bbox":
                wkt = bbox_to_wkt(args.input)
                tile_list_s2 = geom_to_s2_tiles(wkt, args.epsg, filename_tiles_s2)
            elif induced_type == "file":
                aoi_filepath = Path(args.input)
                tile_list_s2 = create_tiles_list_s2(filename_tiles_s2, aoi_filepath)
                dev_logger.info(
                    "Nb of S2 tiles which crossing the AOI: %s",
                        len(tile_list_s2)
                )
            else:
                dev_logger.error("Unrecognized Option: %s",induced_type)

        if not args.s2_only:
            # L8 Tiles
            filename_tiles_l8 = (
                aux_data_dirpath / "wrs2_descending" / "wrs2_descending.shp"
            )
            if induced_type == "wkt":
                wkt = args.input
                tile_list_l8 = geom_to_l8_tiles(wkt, args.epsg, filename_tiles_l8)
            elif induced_type == "location":
                url = f"https://nominatim.openstreetmap.org/search?q={args.input}" \
                      f"&format=geojson&polygon_geojson=1&limit=1"
                data = requests.get(url)
                elt = data.json()
                geom = shape(elt["features"][0]["geometry"])
                tile_list_l8 = create_tiles_list_l8_from_geometry(filename_tiles_l8, geom)
            elif induced_type == "bbox":
                wkt = bbox_to_wkt(args.input)
                tile_list_l8 = geom_to_l8_tiles(wkt, args.epsg, filename_tiles_l8)
            elif induced_type == "file":
                aoi_filepath = Path(args.input)
                tile_list_l8 = create_tiles_list_l8(filename_tiles_l8, aoi_filepath)
                dev_logger.info(
                    "Nb of L8 tiles which crossing the AOI: %s",
                        len(tile_list_l8)
                )
            else:
                dev_logger.error("Unrecognized Option: %s",induced_type)

    # Outputting the result
    if args.to_file is not None:
        output_path = Path(args.to_file)
        if not args.l8_only:
            write_tiles_bb(
                tile_list_s2,
                output_path.with_name(output_path.stem + "_S2" + output_path.suffix),
            )
        if not args.s2_only:
            write_tiles_bb(
                tile_list_l8,
                output_path.with_name(output_path.stem + "_L8" + output_path.suffix),
            )
    elif args.to_wkt:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info("S2 Tile: %s", elt.polyBB.wkt)

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile: %s", elt.polyBB.wkt)
    elif args.to_bbox:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info("S2 Tile Bounds:%s", str(elt.polyBB.bounds))
        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile Bounds: %s", str(elt.polyBB.bounds))
    elif args.to_tile_id:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info("S2 Tile id: %s", str(elt.ID))
        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile id: %s", str(elt.ID))
    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                centroid = list(list(elt.polyBB.centroid.coords)[0])
                centroid.reverse()
                location = geolocator.reverse(centroid)
                if location is not None:
                    user_logger.info(str(location))

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                centroid = list(list(elt.polyBB.centroid.coords)[0])
                centroid.reverse()
                location = geolocator.reverse(centroid)
                if location is not None:
                    user_logger.info(str(location))
    else:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info(str(elt))

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info(str(elt))


if __name__ == "__main__":
    sys.exit(main())
