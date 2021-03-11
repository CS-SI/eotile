# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud, mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

from pathlib import Path
from typing import List, Tuple

from eotile.eotiles.eotiles import (
    get_tile,
    get_tile_s2,
    bbox_to_wkt,
    load_tiles_list_eo,
    load_tiles_list_s2,
    create_tiles_list_eo_from_geometry,
    create_tiles_list_s2_from_geometry,
)
from eotile.eotiles.eotiles import EOTile, S2Tile
import logging
import re

dev_logger = logging.getLogger("dev_logger")


def tile_id_matcher(input_value: str) -> str:
    """
    Induces the type of the input from the user input

    :param input_value: input provided by user of the cli
    :return: type of the input: wkt, bbox, tile_id, file, location
    :rtype: str
    :raises ValueError: when the input value cannot be parsed
    """
    cop_srtm_pattern = "(N|S)([0-9]){2,3}(E|W)([0-9]){2,3}"

    s2_pattern = "([0-9]){2}([A-Z]){3}"

    l8_pattern = "([0-9]){4,6}"

    cop_srtm_reg = re.compile(cop_srtm_pattern)
    s2_reg = re.compile(s2_pattern)
    l8_reg = re.compile(l8_pattern)

    if cop_srtm_reg.match(input_value) and cop_srtm_reg.match(input_value).string == input_value:
        return False, False, True, True

    if s2_reg.match(input_value) and s2_reg.match(input_value).string == input_value:
        return True, False, False, False

    if l8_reg.match(input_value) and l8_reg.match(input_value).string == input_value:
        return False, True, False, False

    raise ValueError(f"Cannot parse this input: {input_value}")


def get_tiles_from_tile_id(
    tile_id: str,
    aux_data_dirpath: Path,
    s2_only: bool,
    l8_only: bool,
    srtm: bool,
    cop: bool,
    min_overlap=None,
) -> Tuple[List[S2Tile], List[EOTile], List[EOTile], List[EOTile]]:
    """Returns the bounding box of a tile designated by its ID.

    :param tile_id: The identifier of the tile
    :param aux_data_dirpath: Path to the input aux data
    :param s2_only: Is he requested tile a Sentinel 2 tile ?
    :type s2_only: Boolean
    :param l8_only: Is he requested tile a Landscape 8 tile ?
    :type l8_only: Boolean
    :param srtm: Should SRTM tiles be used ?
    :type srtm: Boolean
    :param cop: Should Copernicus tiles be used ?
    :type cop: Boolean
    :param min_overlap: (Optional, default = None) Is there a minimum overlap percentage for a tile to be considered
    overlapping ?
    :return: Two lists of tiles
    """

    # s2 tiles grig
    filename_tiles_s2 = (
        Path(aux_data_dirpath)
        / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
    )

    # l8 tiles grid
    filename_tiles_l8 = Path(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
    # SRTM Tiles
    filename_tiles_srtm = aux_data_dirpath / "srtm" / "srtm_grid_1deg.shp"
    # Copernicus Tiles
    filename_tiles_cop = aux_data_dirpath / "Copernicus" / "dem30mGrid.shp"

    [is_s2, is_l8, is_cop, is_srtm] = tile_id_matcher(tile_id)
    output_s2, output_l8, output_srtm, output_cop = [], [], [], []
    tile = None
    if not s2_only and is_l8:
        # Search on l8 Tiles
        tile_list_l8 = load_tiles_list_eo(filename_tiles_l8, "L8")
        output_l8.append(get_tile(tile_list_l8, tile_id))
        tile = output_l8[0]

    if srtm and is_srtm:
        # Search on SRTM Tiles
        tile_list_srtm = load_tiles_list_eo(filename_tiles_srtm, "SRTM")
        output_srtm.append(get_tile(tile_list_srtm, tile_id))
        tile = output_srtm[0]

    if cop and is_cop:
        # Search on Copernicus Tiles
        tile_list_cop = load_tiles_list_eo(filename_tiles_cop, "Copernicus")
        output_cop.append(get_tile(tile_list_cop, tile_id))
        tile = output_cop[0]

    if not l8_only and is_s2:
        # Search on s2 Tiles
        tile_list_s2 = load_tiles_list_s2(filename_tiles_s2)
        output_s2.append(get_tile_s2(tile_list_s2, tile_id))
        tile = output_s2[0]

    try:
        if tile is not None and not is_l8 and not s2_only:
            output_l8 = create_tiles_list_eo_from_geometry(
                filename_tiles_l8, tile.polyBB, "L8", min_overlap
            )
        if tile is not None and not is_s2 and not l8_only:
            output_s2 = create_tiles_list_s2_from_geometry(
                filename_tiles_s2, tile.polyBB, min_overlap
            )
        if tile is not None and not is_srtm and srtm:
            output_srtm = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, tile.polyBB, "SRTM", min_overlap
            )
        if tile is not None and not is_cop and cop:
            output_cop = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, tile.polyBB, "Copernicus", min_overlap
            )
    except (UnboundLocalError, IndexError) as e:
        dev_logger.error(e)
        return [], [], [], []
    return output_s2, output_l8, output_srtm, output_cop
