# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from pathlib import Path

from eotile.eotiles.eotiles import (
    create_tiles_list_l8,
    create_tiles_list_s2,
    write_tiles_bb,
)

LOGGER = logging.getLogger(__name__)


def create_tiles_file_from_aoi(
    aoi_filepath: Path, aux_data_dirpath: Path, out_dirpath: Path, is_s2
):
    """
    Creates Shapefiles containing tiles of each Sentinel 2 and Landscape 8 that are cointained within the AOI given
    in input

    :param aoi_filepath: Path to the input Area Of Interest (must be a shp)
    :type aoi_filepath: Path
    :param aux_data_dirpath: Path to the input aux data
    :type aux_data_dirpath: Path
    :param out_dirpath: Path to write the output files in
    :param is_s2: Is he requested tile a Sentinel 2 tile if not then output a Landscape 8 tile
    :type is_s2: Boolean
    """
    basename_aoi_wt_ext = aoi_filepath.stem
    if is_s2:
        # S2 tiles
        filename_tiles_s2 = (
            Path(aux_data_dirpath)
            / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
        )

        tile_list_s2 = create_tiles_list_s2(filename_tiles_s2, aoi_filepath)

        LOGGER.info(
            "Nb of S2 tiles which crossing the AOI: {}".format(len(tile_list_s2))
        )
        write_tiles_bb(
            tile_list_s2,
            Path(out_dirpath) / (basename_aoi_wt_ext + "_tiles_S2.shp"),
        )
    else:
        # L8 tiles
        filename_tiles_l8 = aux_data_dirpath / "wrs2_descending" / "wrs2_descending.shp"

        tile_list_l8 = create_tiles_list_l8(filename_tiles_l8, aoi_filepath)

        LOGGER.info(
            "Nb of L8 tiles which crossing the AOI: {}".format(len(tile_list_l8))
        )

        write_tiles_bb(
            tile_list_l8, out_dirpath / (basename_aoi_wt_ext + "_tiles_L8.shp")
        )
