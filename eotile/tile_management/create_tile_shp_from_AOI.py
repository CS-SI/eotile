# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import argparse
import logging
import os
import pathlib
import sys

from eotile.utils.tile_list_utils import *

LOGGER = logging.getLogger(__name__)


def create_tiles_file_from_AOI(aoi_filepath, aux_data_dirpath, out_dirpath, s2, l8):
    """
    Creates Shapefiles containing tiles of each Sentinel 2 and Landscape 8 that are cointained within the AOI given
    in input

    :param aoi_filepath: Path to the input Area Of Interest (must be a shp)
    :type aoi_filepath: String
    :param aux_data_dirpath: Path to the input aux data
    :type aux_data_dirpath: String
    :param out_dirpath: Path to write the output files in
    """
    basenameAOI_wt_ext = pathlib.Path(aoi_filepath).stem

    # S2 tiles
    filename_tiles_S2 = str(
        pathlib.PurePath(aux_data_dirpath)
        / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
    )

    tile_list_S2 = create_tiles_list_S2(filename_tiles_S2, aoi_filepath)

    LOGGER.info("Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list_S2)))
    write_tiles_bb(
        tile_list_S2,
        str(pathlib.PurePath(out_dirpath) / (basenameAOI_wt_ext + "_tiles_S2.shp")),
    )

    # L8 tiles
    filename_tiles_L8 = str(
        pathlib.PurePath(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
    )

    tile_list_L8 = create_tiles_list_L8(filename_tiles_L8, aoi_filepath)

    LOGGER.info("Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list_L8)))

    write_tiles_bb(
        tile_list_L8,
        str(pathlib.PurePath(out_dirpath) / (basenameAOI_wt_ext + "_tiles_L8.shp")),
        sensor="L8",
    )


def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("aoi_filepath", help="aoi filepath")
    parser.add_argument("auxdata_dirpath", help="path to the aux data directory")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument(
        "-s2", action="store_true", help="output S2 tiles which intersect the aoi"
    )
    parser.add_argument(
        "-l8", action="store_true", help="output L8 tiles which intersect the aoi"
    )
    return parser


def main(arguments=None):
    """
    Command line interface to perform the creation of files which containt the S2 or L8 tiles
    chich intersect the aoi

    :param arguments: list of arguments
    :type arguments: list
    """

    arg_parser = build_parser()

    args = arg_parser.parse_args(args=arguments)

    create_tiles_file_from_AOI(
        args.aoi_filepath, args.auxdata_dirpath, args.out_dir, args.s2, args.l8
    )


if __name__ == "__main__":
    sys.exit(main())
