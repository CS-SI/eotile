# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

from pathlib import Path
from typing import List, Tuple

from eotile.eotiles.eotiles import (
    get_tile,
    bbox_to_wkt,
    geom_to_s2_tiles,
    geom_to_eo_tiles,
    create_tiles_list_eo_from_geometry,
    create_tiles_list_s2_from_geometry,
)
from eotile.eotiles.eotiles import EOTile, S2Tile




def get_tiles_from_tile_id(
    tile_id: str, aux_data_dirpath: Path, s2_only: bool, l8_only: bool, srtm: bool, cop: bool, min_overlap=None
) -> Tuple[List[S2Tile], List[EOTile], List[EOTile], List[EOTile]]:
    """Returns the bounding box of a tile designated by its ID.

    :param tile_id: The identifier of the tile
    :param aux_data_dirpath: Path to the input aux data
    :param s2_only: Is he requested tile a Sentinel 2 tile ?
    :type s2_only: Boolean
    :param l8_only: Is he requested tile a Landscape 8 tile ?
    :type l8_only: Boolean
    :return: Two lists of tiles
    """

    # s2 tiles grig
    filename_tiles_s2 = (
        Path(aux_data_dirpath)
        / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
    )

    # l8 tiles grid
    filename_tiles_l8 = (
        Path(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
    )
    # SRTM Tiles
    filename_tiles_srtm = (
            aux_data_dirpath / "srtm" / "srtm_grid_1deg.shp"
    )
    # Copernicus Tiles
    filename_tiles_cop = (
            aux_data_dirpath / "Copernicus" / "dem30mGrid.shp"
    )
    check_bb_on_s2, check_bb_on_l8, check_bb_on_srtm, check_bb_on_cop = False, False, False, False

    wkt = bbox_to_wkt(["-90", "90", "-180", "180"])
    output_s2, output_l8, output_srtm, output_cop = [], [], [], []
    tile = None
    if not s2_only:
        # Search on l8 Tiles
        tile_list_l8 = geom_to_eo_tiles(wkt, None, filename_tiles_l8, "L8")
        try:
            output_l8.append(get_tile(tile_list_l8, tile_id))
            tile = output_l8[0]
        except (
            KeyError,
            ValueError,
        ):  # In this case, the key does not exist so we output empty
            if not l8_only or srtm or cop:
                check_bb_on_l8 = True

    if srtm:
        # Search on SRTM Tiles
        tile_list_srtm = geom_to_eo_tiles(wkt, None, filename_tiles_srtm, "SRTM")
        try:
            output_srtm.append(get_tile(tile_list_srtm, tile_id))
            tile = output_srtm[0]
        except (
            KeyError,
            ValueError,
        ):  # In this case, the key does not exist so we output empty
            check_bb_on_srtm = True

    if cop:
        # Search on Copernicus Tiles
        tile_list_cop = geom_to_eo_tiles(wkt, None, filename_tiles_cop, "Copernicus")
        try:
            output_cop.append(get_tile(tile_list_cop, tile_id))
            tile = output_cop[0]
        except (
            KeyError,
            ValueError,
        ):  # In this case, the key does not exist so we output empty
            check_bb_on_cop = True

    if not l8_only:
        # Search on s2 Tiles
        tile_list_s2 = geom_to_s2_tiles(wkt, None, filename_tiles_s2)
        try:
            output_s2.append(get_tile(tile_list_s2, tile_id))
            tile = output_s2[0]
        except (
            KeyError,
            ValueError,
        ):  # In this case, the key does not exist so we output empty
            if not s2_only or srtm or cop:
                check_bb_on_s2 = True
    try:
        if check_bb_on_l8:
            output_l8 = create_tiles_list_eo_from_geometry(
                filename_tiles_l8, tile.polyBB, "L8", min_overlap
            )
        if check_bb_on_s2:
            output_s2 = create_tiles_list_s2_from_geometry(
                filename_tiles_s2, tile.polyBB, min_overlap
            )
        if check_bb_on_srtm:
            output_srtm = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, tile.polyBB, "SRTM", min_overlap
            )
        if check_bb_on_cop:
            output_cop = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, tile.polyBB, "Copernicus", min_overlap
            )
    except (UnboundLocalError, IndexError):
        return [], [], [], []
    return output_s2, output_l8, output_srtm, output_cop
