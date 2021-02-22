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
from eotile.eotile.create_tile_shp_from_AOI import create_tiles_file_from_AOI
from eotile.eotiles.eotiles import create_tiles_list_L8, create_tiles_list_S2, create_tiles_list_S2_from_geometry
import sys
import geopandas as gp
import pathlib
from osgeo import ogr, osr

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

    print(args.input) # DEBUG

    with open("config/data_path") as conf_file:
        data_path = conf_file.readline()

    print(data_path) # DEBUG
    aux_data_dirpath = data_path.strip()

    if args.input[0] == 'wkt':

        wkt = args.input[1]
        if args.s2_only:
            # S2 tiles
            filename_tiles_S2 = str(
                pathlib.PurePath(aux_data_dirpath)
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            geom = ogr.CreateGeometryFromWkt(wkt)

            # Projection Transformation if any
            if args.epsg is not None:
                source = osr.SpatialReference()
                source.ImportFromEPSG(int(args.epsg))
                target = osr.SpatialReference()
                target.ImportFromEPSG(4326)
                transform = osr.CoordinateTransformation(source, target)
                geom.Transform(transform)
                print(geom.ExportToWkt())


            tile_list = create_tiles_list_S2_from_geometry(filename_tiles_S2,
                                       geom)

    if args.input[0] == 'bbox':
        if args.s2_only:
            # S2 tiles
            filename_tiles_S2 = str(
                pathlib.PurePath(aux_data_dirpath)
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            [ulx, uly, lrx, lry] = args.input[1]
            wkt = f"""
            POLYGON (({ulx},{uly},
            {ulx},{lry},
            {lrx},{lry},
            {lrx},{uly},
            {ulx},{uly}))
            """
            geom = ogr.CreateGeometryFromWkt(wkt)

            # Projection Transformation if any
            if args.epsg is not None:
                source = osr.SpatialReference()
                source.ImportFromEPSG(int(args.epsg))
                target = osr.SpatialReference()
                target.ImportFromEPSG(4326)
                transform = osr.CoordinateTransformation(source, target)
                geom.Transform(transform)
                print(geom.ExportToWkt())


            tile_list = create_tiles_list_S2_from_geometry(filename_tiles_S2,
                                       geom)

    if args.input[0] == 'file':
        aoi_filepath = args.input[1]
        basenameAOI_wt_ext = pathlib.Path(aoi_filepath).stem
        if args.s2_only:
            # S2 tiles
            filename_tiles_S2 = str(
                pathlib.PurePath(aux_data_dirpath)
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            print(filename_tiles_S2)
            print(basenameAOI_wt_ext)
            tile_list = create_tiles_list_S2(filename_tiles_S2, aoi_filepath)

            LOGGER.info("Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list)))

        else:
            # L8 tiles
            filename_tiles_L8 = str(
                pathlib.PurePath(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
            )

            tile_list = create_tiles_list_L8(filename_tiles_L8, aoi_filepath)

            LOGGER.info("Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list)))

    for elt in tile_list:
        elt.display()

if __name__ == "__main__":
    sys.exit(main())