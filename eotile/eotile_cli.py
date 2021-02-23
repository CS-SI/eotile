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
from eotile.eotiles.eotiles import create_tiles_list_L8, create_tiles_list_S2, create_tiles_list_S2_from_geometry,\
    get_tile, create_tiles_list_L8_from_geometry
import sys
import pathlib
from osgeo import ogr, osr
from geopy.geocoders import Nominatim

def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Choose amongst :\n - file\n - tile_id\n - location\n - wkt\n - bbox",
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

    if not args.l8_only:
        # S2 Tiles
        filename_tiles_S2 = str(
            pathlib.PurePath(aux_data_dirpath)
            / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
        )
        if args.input[0] == 'wkt':
            wkt = args.input[1]
            tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
        if args.input[0] == 'location':
            geolocator = Nominatim(user_agent="EOTile")
            location = geolocator.geocode(args.input[1])
            wkt = bbox_to_wkt(location.raw["boundingbox"])
            tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
        if args.input[0] == 'bbox':
            wkt = bbox_to_wkt(args.input[1])
            tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
        if args.input[0] == 'file':
            aoi_filepath = args.input[1]
            tile_list_s2 = create_tiles_list_S2(filename_tiles_S2, aoi_filepath)
            LOGGER.info("Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list_s2)))
        if args.input[0] == 'tile_id':
            wkt = bbox_to_wkt(['-90', '90', '-180', '180'])
            tile_list_s2 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_S2)
            try:
                tile_list_s2 = [get_tile(tile_list_s2, args.input[1])]
            except KeyError: # In this case, the key does not exist so we output empty
                tile_list_s2 = []
    if not args.s2_only:
    # L8 Tiles
        filename_tiles_L8 = str(
            pathlib.PurePath(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
        )
        if args.input[0] == 'wkt':
            wkt = args.input[1]
            tile_list_l8 = geom_to_S2_tiles(wkt, args.epsg, filename_tiles_L8)
        if args.input[0] == 'location':
            geolocator = Nominatim(user_agent="EOTile")
            location = geolocator.geocode(args.input[1])
            wkt = bbox_to_wkt(location.raw["boundingbox"])
            tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
        if args.input[0] == 'bbox':
            wkt = bbox_to_wkt(args.input[1])
            tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
        if args.input[0] == 'file':
            aoi_filepath = args.input[1]
            tile_list_l8 = create_tiles_list_L8(filename_tiles_L8, aoi_filepath)
            LOGGER.info("Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list_l8)))
        if args.input[0] == 'tile_id':
            wkt = bbox_to_wkt(['-90', '90', '-180', '180'])
            tile_list_l8 = geom_to_L8_tiles(wkt, args.epsg, filename_tiles_L8)
            try:
                tile_list_l8 = [get_tile(tile_list_l8, args.input[1])]
            except KeyError: # In this case, the key does not exist so we output empty
                tile_list_l8 = []

    if len(tile_list_s2) > 0:
        print("--- S2 Tiles ---")
        for elt in tile_list_s2:
            elt.display()

    if len(tile_list_l8) > 0:
        print("--- L8 Tiles ---")
        for elt in tile_list_l8:
            elt.display()


def bbox_to_wkt(bbox_list):
    if type(bbox_list) == str:
        bbox_list = bbox_list.replace("[", "")
        bbox_list = bbox_list.replace("]", "")
        bbox_list = bbox_list.replace("'", "")
        bbox_list = list(bbox_list.split(","))
    [ul_lat, lr_lat, ul_long, lr_long] = [float(elt) for elt in bbox_list]
    return(f"POLYGON (({ul_long} {ul_lat}, {lr_long} {ul_lat}, {lr_long} {lr_lat},\
     {ul_long} {lr_lat}, {ul_long} {ul_lat} ))")


def geom_to_S2_tiles(wkt, epsg, filename_tiles_S2):
    geom = ogr.CreateGeometryFromWkt(wkt)
    # Projection Transformation if any
    if epsg is not None:
        source = osr.SpatialReference()
        source.ImportFromEPSG(int(epsg))
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(source, target)
        geom.Transform(transform)
    return create_tiles_list_S2_from_geometry(filename_tiles_S2, geom)


def geom_to_L8_tiles(wkt, epsg, filename_tiles_S2):
    geom = ogr.CreateGeometryFromWkt(wkt)
    # Projection Transformation if any
    if epsg is not None:
        source = osr.SpatialReference()
        source.ImportFromEPSG(int(epsg))
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(source, target)
        geom.Transform(transform)
    return create_tiles_list_L8_from_geometry(filename_tiles_S2, geom)

if __name__ == "__main__":
    sys.exit(main())