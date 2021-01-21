# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import argparse
import os
import sys

from tile_list_utils import *

def create_tiles_file_from_AOI(aoi_filepath, aux_data_dirpath, out_dirpath, s2, l8):

    basenameAOI_wt_ext=os.path.splitext(os.path.basename(aoi_filepath))[0]

    #S2 tiles
    filename_tiles_S2=os.path.join(aux_data_dirpath,
                                'S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml')

    tile_list_S2 = create_tiles_list_S2(filename_tiles_S2, aoi_filepath)

    print("Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list_S2)))

    write_tiles_bb(tile_list_S2, 
                   os.path.join(out_dirpath, basenameAOI_wt_ext + '_tiles_S2.shp'))

    #L8 tiles
    filename_tiles_L8=os.path.join(aux_data_dirpath,'wrs2_descending','wrs2_descending.shp')

    tile_list_L8 = create_tiles_list_L8(filename_tiles_L8, aoi_filepath)

    print("Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list_L8)))

    write_tiles_bb(tile_list_L8,
                   os.path.join(out_dirpath, basenameAOI_wt_ext + '_tiles_L8.shp'),
                   sensor='L8')

def build_parser():
    '''Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("aoi_filepath", help="aoi filepath")
    parser.add_argument("auxdata_dirpath", help="path to the srtm directory")
    parser.add_argument("out_dir",
                        help="output directory")
    parser.add_argument("-s2", action='store_true',
                        help="output S2 tiles which intersect the aoi")
    parser.add_argument("-l8", action='store_true',
                        help="output L8 tiles which intersect the aoi")
    return parser


def main(arguments=None):
    '''
    Command line interface to perform the creation of files which containt the S2 or L8 tiles
    chich intersect the aoi 

    :param list arguments: list of arguments
    '''

    arg_parser = build_parser()

    args = arg_parser.parse_args(args=arguments)
   
    create_tiles_file_from_AOI(args.aoi_filepath,
                               args.auxdata_dirpath,
                               args.out_dir,
                               args.s2,
                               args.l8)

if __name__ == "__main__":
    sys.exit(main())
