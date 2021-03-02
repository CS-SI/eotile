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

from geopy.geocoders import Nominatim

from eotile.eotiles.eotiles import (
    bbox_to_wkt,
    create_tiles_list_l8,
    create_tiles_list_s2,
    geom_to_l8_tiles,
    geom_to_s2_tiles,
    write_tiles_bb,
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

def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Choose amongst : file, tile_id, location, wkt, bbox. Then specify the argument",
        nargs=2,
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

    import pkg_resources
    with open(pkg_resources.resource_filename(__name__, 'config/data_path')) as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = Path(pkg_resources.resource_filename(__name__, data_path.strip()))
    tile_list_s2, tile_list_l8 = [], []
    if args.input[0] == "tile_id":
        tile_list_s2, tile_list_l8 = get_tiles_from_tile_id(
            args.input[1], aux_data_dirpath, args.s2_only, args.l8_only
        )
    else:
        if not args.l8_only:
            # S2 Tiles
            filename_tiles_s2 = (
                aux_data_dirpath
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            if args.input[0] == "wkt":
                wkt = args.input[1]
                tile_list_s2 = geom_to_s2_tiles(wkt, args.epsg, filename_tiles_s2)
            elif args.input[0] == "location":
                geolocator = Nominatim(user_agent="EOTile")
                location = geolocator.geocode(args.input[1])
                wkt = bbox_to_wkt(location.raw["boundingbox"])
                tile_list_s2 = geom_to_s2_tiles(wkt, args.epsg, filename_tiles_s2)
            elif args.input[0] == "bbox":
                wkt = bbox_to_wkt(args.input[1])
                tile_list_s2 = geom_to_s2_tiles(wkt, args.epsg, filename_tiles_s2)
            elif args.input[0] == "file":
                aoi_filepath = Path(args.input[1])
                tile_list_s2 = create_tiles_list_s2(filename_tiles_s2, aoi_filepath)
                dev_logger.info(
                    "Nb of S2 tiles which crossing the AOI: {}".format(
                        len(tile_list_s2)
                    )
                )
            else:
                dev_logger.error(f"Unrecognized Option : {args.input[0]}")

        if not args.s2_only:
            # L8 Tiles
            filename_tiles_l8 = (
                aux_data_dirpath / "wrs2_descending" / "wrs2_descending.shp"
            )
            if args.input[0] == "wkt":
                wkt = args.input[1]
                tile_list_l8 = geom_to_l8_tiles(wkt, args.epsg, filename_tiles_l8)
            elif args.input[0] == "location":
                geolocator = Nominatim(user_agent="EOTile")
                location = geolocator.geocode(args.input[1])
                wkt = bbox_to_wkt(location.raw["boundingbox"])
                tile_list_l8 = geom_to_l8_tiles(wkt, args.epsg, filename_tiles_l8)
            elif args.input[0] == "bbox":
                wkt = bbox_to_wkt(args.input[1])
                tile_list_l8 = geom_to_l8_tiles(wkt, args.epsg, filename_tiles_l8)
            elif args.input[0] == "file":
                aoi_filepath = Path(args.input[1])
                tile_list_l8 = create_tiles_list_l8(filename_tiles_l8, aoi_filepath)
                dev_logger.info(
                    "Nb of L8 tiles which crossing the AOI: {}".format(
                        len(tile_list_l8)
                    )
                )
            else:
                dev_logger.error(f"Unrecognized Option : {args.input[0]}")

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
                user_logger.info("S2 Tile: " + elt.polyBB.wkt + "\n")

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile: " + elt.polyBB.wkt + "\n")
    elif args.to_bbox:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info("S2 Tile Bounds: " + str(elt.polyBB.bounds) + "\n")
        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile Bounds: " + str(elt.polyBB.bounds) + "\n")
    elif args.to_tile_id:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info("S2 Tile id: " + str(elt.ID) + "\n")
        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info("L8 Tile id: " + str(elt.ID) + "\n")
    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                centroid = list(list(elt.polyBB.centroid.coords)[0])
                centroid.reverse()
                location = geolocator.reverse(centroid)
                if location is not None:
                    user_logger.info(str(location) + "\n")

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                centroid = list(list(elt.polyBB.centroid.coords)[0])
                centroid.reverse()
                location = geolocator.reverse(centroid)
                if location is not None:
                    user_logger.info(str(location) + "\n")
    else:
        if len(tile_list_s2) > 0:
            for elt in tile_list_s2:
                user_logger.info(str(elt))

        if len(tile_list_l8) > 0:
            for elt in tile_list_l8:
                user_logger.info(str(elt))


if __name__ == "__main__":
    sys.exit(main())
