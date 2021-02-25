# -*- coding: utf-8 -*-
"""
EO tile

:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import argparse
from eotile.eotiles.eotiles import create_tiles_list_L8, create_tiles_list_S2, write_tiles_bb, \
    bbox_to_wkt, geom_to_S2_tiles, geom_to_L8_tiles
import sys
from pathlib import PurePath
from geopy.geocoders import Nominatim
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id

def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Choose amongst : file, tile_id, location, wkt, bbox. Then specify the argument",
                        nargs=2)
    parser.add_argument(
        "-epsg", help="Specify the epsg of the input"
    )
    parser.add_argument(
        "-s2_only", action="store_true", help="output S2 tiles which intersect the aoi"
    )
    parser.add_argument(
        "-l8_only", action="store_true", help="output L8 tiles which intersect the aoi"
    )

    # Output arguments

    parser.add_argument(
        "-to_file", help="Write tiles to a file"
    )
    parser.add_argument(
        "-to_wkt", action="store_true", help="Output the geometry of matching tiles with wkt format on standard output"
    )
    parser.add_argument(
        "-to_bbox", action="store_true", help="Output the bounding box of matching tiles on standard output"
    )
    parser.add_argument(
        "-to_tile_id", action="store_true", help="Output the id(s) of matching tiles on standard output"
    )
    parser.add_argument(
        "-to_location", action="store_true", help="Output the location of the centroid of matching tiles "
                                                  "on standard output"
    )
    return parser


def main(arguments=None):
    """
    Command line interface to perform

    :param list arguments: list of arguments
    """
    logging.basicConfig(filename="eotile_cli.log", level=logging.INFO)
    LOGGER = logging.getLogger(__name__)

    arg_parser = build_parser()

    args = arg_parser.parse_args(args=arguments)

    with open("config/data_path") as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = data_path.strip()
    tile_list_s2, tile_list_l8 = [], []
    if args.input[0] == 'tile_id' :
        tile_list_s2, tile_list_l8 = get_tiles_from_tile_id(args.input[1], aux_data_dirpath, args.s2_only, args.l8_only)
    else :
        if not args.l8_only:
            # S2 Tiles
            filename_tiles_S2 = str(
                PurePath(aux_data_dirpath)
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            if args.input[0] == 'wkt':
                wkt = args.input[1]
                tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
            elif args.input[0] == 'location':
                geolocator = Nominatim(user_agent="EOTile")
                location = geolocator.geocode(args.input[1])
                wkt = bbox_to_wkt(location.raw["boundingbox"])
                tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
            elif args.input[0] == 'bbox':
                wkt = bbox_to_wkt(args.input[1])
                tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
            elif args.input[0] == 'file':
                aoi_filepath = args.input[1]
                tile_list_s2 = create_tiles_list_S2(filename_tiles_S2, aoi_filepath)
                LOGGER.info("Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list_s2)))
            else:
                print(f"Unrecognized Option : {args.input[0]}")

        if not args.s2_only:
        # L8 Tiles
            filename_tiles_L8 = str(
                PurePath(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
            )
            if args.input[0] == 'wkt':
                wkt = args.input[1]
                tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
            elif args.input[0] == 'location':
                geolocator = Nominatim(user_agent="EOTile")
                location = geolocator.geocode(args.input[1])
                wkt = bbox_to_wkt(location.raw["boundingbox"])
                tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
            elif args.input[0] == 'bbox':
                wkt = bbox_to_wkt(args.input[1])
                tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
            elif args.input[0] == 'file':
                aoi_filepath = args.input[1]
                tile_list_l8 = create_tiles_list_L8(filename_tiles_L8, aoi_filepath)
                LOGGER.info("Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list_l8)))
            else:
                print(f"Unrecognized Option : {args.input[0]}")

    # Ouptuting the result
    if args.to_file is not None:
        write_tiles_bb(tile_list_s2, args.to_file)
        write_tiles_bb(tile_list_l8, args.to_file)
    elif args.to_wkt:
        if len(tile_list_s2) > 0:
            print("--- S2 Tiles ---")
            for elt in tile_list_s2:
                print(elt.polyBB.wkt)

        if len(tile_list_l8) > 0:
            print("--- L8 Tiles ---")
            for elt in tile_list_l8:
                print(elt.polyBB.wkt)
    elif args.to_bbox:
        if len(tile_list_s2) > 0:
            print("--- S2 Tiles ---")
            for elt in tile_list_s2:
                print(elt.polyBB.bounds)

        if len(tile_list_l8) > 0:
            print("--- L8 Tiles ---")
            for elt in tile_list_l8:
                print(elt.polyBB.bounds)
    elif args.to_tile_id:
        if len(tile_list_s2) > 0:
            print("--- S2 Tiles ---")
            for elt in tile_list_s2:
                print(elt.ID)

        if len(tile_list_l8) > 0:
            print("--- L8 Tiles ---")
            for elt in tile_list_l8:
                print(elt.ID)
    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        if len(tile_list_s2) > 0:
            print("--- S2 Tiles ---")
            for elt in tile_list_s2:
                centroid = list(elt.polyBB.Centroid().GetPoint()[:2])
                centroid.reverse()
                print(geolocator.reverse(tuple(centroid)))

        if len(tile_list_l8) > 0:
            print("--- L8 Tiles ---")
            for elt in tile_list_l8:
                centroid = list(elt.polyBB.Centroid().GetPoint()[:2])
                centroid.reverse()
                print(geolocator.reverse(tuple(centroid)))
    else :
        if len(tile_list_s2) > 0:
            print("--- S2 Tiles ---")
            for elt in tile_list_s2:
                elt.display()

        if len(tile_list_l8) > 0:
            print("--- L8 Tiles ---")
            for elt in tile_list_l8:
                elt.display()


if __name__ == "__main__":
    sys.exit(main())