# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS Group.
#
# This file is part of EOTile.
# See https://github.com/CS-SI/eotile for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Generate tile list according AOI

:author: jsiefert, msavinaud, mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

from pathlib import Path
from typing import Tuple, List
import geopandas as gp
from eotile.eotiles.eotiles import (
    get_tile,
    load_tiles_list_eo,
    create_tiles_list_eo_from_geometry)
import logging
import re
import pandas as pd
from shapely.ops import cascaded_union

dev_logger = logging.getLogger("dev_logger")


def tile_id_matcher(input_value: str) -> Tuple[bool, bool, bool, bool]:
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
        tile_id_list: List,
        aux_data_dirpath: Path,
        s2_only: bool,
        l8_only: bool,
        srtm: bool,
        cop: bool,
        min_overlap=None,
) -> Tuple[gp.GeoDataFrame, gp.GeoDataFrame, gp.GeoDataFrame, gp.GeoDataFrame]:
    """Returns the bounding box of a tile designated by its ID.

    :param tile_id_list: The identifier of the tile
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

    filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"
    filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
    filename_tiles_srtm = aux_data_dirpath / "srtm_tiles.gpkg"
    filename_tiles_cop = aux_data_dirpath / "cop_tiles.gpkg"

    [is_s2, is_l8, is_cop, is_srtm] = tile_id_matcher(tile_id_list[0])
    output_s2, output_l8, output_srtm, output_cop = gp.GeoDataFrame(), gp.GeoDataFrame(), \
                                                    gp.GeoDataFrame(), gp.GeoDataFrame()
    tile = None
    pd.options.mode.chained_assignment = None
    if not s2_only and is_l8:
        # Search on l8 Tiles
        tile_list_l8 = load_tiles_list_eo(filename_tiles_l8)
        for tile_id in tile_id_list:
            tile = get_tile(tile_list_l8, tile_id)
            output_l8 = output_l8.append(tile)
        geometry = cascaded_union(output_l8.geometry)

    if srtm and is_srtm:
        # Search on SRTM Tiles
        tile_list_srtm = load_tiles_list_eo(filename_tiles_srtm)
        for tile_id in tile_id_list:
            tile = get_tile(tile_list_srtm, tile_id)
            output_srtm = output_srtm.append(tile)
        geometry = cascaded_union(output_srtm.geometry)

    if cop and is_cop:
        # Search on Copernicus Tiles
        tile_list_cop = load_tiles_list_eo(filename_tiles_cop)
        for tile_id in tile_id_list:
            tile = get_tile(tile_list_cop, tile_id)
            output_cop = output_cop.append(tile)
        geometry = cascaded_union(output_cop.geometry)

    if not l8_only and is_s2:
        # Search on s2 Tiles
        tile_list_s2 = load_tiles_list_eo(filename_tiles_s2)
        for tile_id in tile_id_list:
            tile = get_tile(tile_list_s2, tile_id)
            output_s2 = output_s2.append(tile)
        geometry = cascaded_union(output_s2.geometry)

    try:
        if tile is not None and not is_l8 and not s2_only:
            output_l8 = create_tiles_list_eo_from_geometry(
                filename_tiles_l8, geometry, min_overlap
            )
        if tile is not None and not is_s2 and not l8_only:
            output_s2 = create_tiles_list_eo_from_geometry(
                filename_tiles_s2, geometry, min_overlap
            )
        if tile is not None and not is_srtm and srtm:
            output_srtm = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, geometry, min_overlap
            )
        if tile is not None and not is_cop and cop:
            output_cop = create_tiles_list_eo_from_geometry(
                filename_tiles_srtm, geometry, min_overlap
            )
    except (UnboundLocalError, IndexError) as e:
        dev_logger.error(e)
        return gp.GeoDataFrame(), gp.GeoDataFrame(), gp.GeoDataFrame(), gp.GeoDataFrame()
    return output_s2, output_l8, output_srtm, output_cop
