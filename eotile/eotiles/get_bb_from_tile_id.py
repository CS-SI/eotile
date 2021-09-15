# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS GROUP - France.
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
:organization: CS GROUP - France
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

from pathlib import Path
from typing import Tuple, List
import geopandas as gp
from eotile.eotiles.eotiles import (
    get_tile,
    load_tiles_list_eo,
    create_tiles_list_eo_from_geometry,
)
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
    dem_pattern = "(N|S)([0-9]){2,3}(E|W)([0-9]){2,3}"

    srtm_5x5_pattern = "srtm_([0-9]){2}_([0-9]){2}"

    s2_pattern = "([0-9]){2}([A-Z]){3}"

    l8_pattern = "([0-9]){4,6}"

    dem_reg = re.compile(dem_pattern)
    s2_reg = re.compile(s2_pattern)
    l8_reg = re.compile(l8_pattern)
    srtm_5x5_reg = re.compile(srtm_5x5_pattern)

    is_dem = (dem_reg.match(input_value) is not None) and dem_reg.match(input_value).string == input_value
    is_s2 = (s2_reg.match(input_value) is not None) and s2_reg.match(input_value).string == input_value
    is_l8 = (l8_reg.match(input_value) is not None) and l8_reg.match(input_value).string == input_value
    is_srtm_5x5 = (srtm_5x5_reg.match(input_value) is not None) \
                  and srtm_5x5_reg.match(input_value).string == input_value

    return_list = [is_s2, is_l8, is_dem, is_srtm_5x5]
    if sum(return_list) == 1:
        return return_list
    else:
        raise ValueError(f"Cannot parse this input: {input_value} ({return_list})")


def build_reference_geom(file_name, tile_id_list):
    output = gp.GeoDataFrame()

    tile_list = load_tiles_list_eo(file_name)

    for tile_id in tile_id_list:
        tile = get_tile(tile_list, tile_id)
        output = output.append(tile)

    geometry = cascaded_union(list(output.geometry))

    return tile, geometry, output


def get_tiles_from_tile_id(
        tile_id_list: List,
        aux_data_dirpath: Path,
        s2_only: bool,
        l8_only: bool,
        dem: bool,
        srtm5x5: bool,
        min_overlap=None,
        overlap=False,
) -> Tuple[gp.GeoDataFrame, gp.GeoDataFrame, gp.GeoDataFrame, gp.GeoDataFrame]:
    """Returns the bounding box of a tile designated by its ID.

    :param tile_id_list: The identifier of the tile
    :param aux_data_dirpath: Path to the input aux data
    :param s2_only: Is he requested tile a Sentinel 2 tile ?
    :type s2_only: Boolean
    :param l8_only: Is he requested tile a Landscape 8 tile ?
    :type l8_only: Boolean
    :param dem: Should DEM tiles be used ?
    :type dem: Boolean
    :param srtm5x5: Should Specific SRTM 5x5 tiles be used ?
    :type srtm5x5: Boolean
    :param min_overlap: (Optional, default = None) Is there a minimum overlap percentage for a
    tile to be considered overlapping ?
    :param overlap: (Optional, default = False) Do you want to use the overlapping source file ?
    :type overlap: Boolean
    :return: Two lists of tiles
    """
    if not overlap:
        filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"

    else:
        filename_tiles_s2 = aux_data_dirpath / "s2_with_overlap.gpkg"

    filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
    filename_tiles_srtm5x5 = aux_data_dirpath / "srtm5x5_tiles.gpkg"
    filename_tiles_dem = aux_data_dirpath / "DEM_Union.gpkg"

    [is_s2, is_l8, is_dem, is_srtm5x5] = tile_id_matcher(tile_id_list[0])

    tile = None
    pd.options.mode.chained_assignment = None
    if is_l8:
        # Search on L8 Tiles
        tile, geometry, output_l8 = build_reference_geom(filename_tiles_l8, tile_id_list)

    if is_dem:
        # Search on DEM Tiles
        tile, geometry, output_dem = build_reference_geom(filename_tiles_dem, tile_id_list)

    if is_srtm5x5:
        # Search on specific SRTM 5x5 Tiles
        tile, geometry, output_srtm5x5 = build_reference_geom(filename_tiles_srtm5x5, tile_id_list)

    if is_s2:
        # Search on s2 Tiles
        tile, geometry, output_s2 = build_reference_geom(filename_tiles_s2, tile_id_list)

    try:
        if tile is not None:
            if not is_l8 and not s2_only:
                output_l8 = create_tiles_list_eo_from_geometry(
                    filename_tiles_l8, geometry, min_overlap
                )
            if not is_s2 and not l8_only:
                output_s2 = create_tiles_list_eo_from_geometry(
                    filename_tiles_s2, geometry, min_overlap
                )
            if not is_dem and dem:
                output_dem = create_tiles_list_eo_from_geometry(
                    filename_tiles_dem, geometry, min_overlap
                )
            if not is_srtm5x5 and srtm5x5:
                output_srtm5x5 = create_tiles_list_eo_from_geometry(
                    filename_tiles_srtm5x5, geometry, min_overlap
                )
    except (UnboundLocalError, IndexError) as e:
        dev_logger.error(e)
        return gp.GeoDataFrame(), gp.GeoDataFrame(), gp.GeoDataFrame(), gp.GeoDataFrame()

    if not dem:
        output_dem = gp.GeoDataFrame()
    if not srtm5x5:
        output_srtm5x5 = gp.GeoDataFrame()
    if s2_only:
        output_l8 = gp.GeoDataFrame()
    if l8_only:
        output_s2 = gp.GeoDataFrame()
    return output_s2, output_l8, output_dem, output_srtm5x5
