# -*- coding: utf-8 -*-
"""
Generate tile list according AOI

:author: jsiefert, msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

from pathlib import PurePath
from eotile.eotiles.eotiles import get_tile, bbox_to_wkt, geom_to_S2_tiles, geom_to_L8_tiles,\
    create_tiles_list_L8_from_geometry, create_tiles_list_S2_from_geometry
from eotile.eotiles.eotiles import L8Tile, S2Tile


def get_tiles_from_tile_id(tile_id, aux_data_dirpath, s2_only, l8_only):
    """Returns the bounding box of a tile designated by its ID.

    :param tile_id: The identifier of the tile
    :param aux_data_dirpath: Path to the input aux data
    :param s2_only: Is he requested tile a Sentinel 2 tile ?
    :type s2_only: Boolean
    :param l8_only: Is he requested tile a Landscape 8 tile ?
    :type l8_only: Boolean
    :return: Two lists of tiles
    :rtype: #TODO: Precise this
    """

    # S2 tiles grig
    filename_tiles_S2 = str(
                PurePath(aux_data_dirpath)
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )

    # L8 tiles grid
    filename_tiles_L8 = str(
        PurePath(aux_data_dirpath) / "wrs2_descending" / "wrs2_descending.shp"
    )
    check_bb_on_s2, check_bb_on_l8 = False, False

    tiles = [] # Contains tiles of the superimposable source
    wkt = bbox_to_wkt(['-90', '90', '-180', '180'])
    if not s2_only:
        # Search on L8 Tiles
        tile_list_l8 = geom_to_L8_tiles(wkt, None, filename_tiles_L8)
        try:
            tile = get_tile(tile_list_l8, int(tile_id))
        except (KeyError, ValueError):  # In this case, the key does not exist so we output empty
            check_bb_on_l8 = True
    if not l8_only:
        # Search on S2 Tiles
        tile_list_s2 = geom_to_S2_tiles(wkt, None, filename_tiles_S2)

        try:
            tile = get_tile(tile_list_s2, tile_id)
        except (KeyError, ValueError):  # In this case, the key does not exist so we output empty
            check_bb_on_s2 = True
    try:
        if check_bb_on_l8:
            tiles = create_tiles_list_L8_from_geometry(filename_tiles_L8, tile.polyBB)
            return [tile], tiles
        elif check_bb_on_s2:
            tiles = create_tiles_list_S2_from_geometry(filename_tiles_S2, tile.polyBB)
            return tiles, [tile]
    except UnboundLocalError:
        return [], []
