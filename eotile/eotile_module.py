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
EO tile

:author: mgerma
:organization: CS GROUP - France
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from pathlib import Path

import pkg_resources

from eotile.eotiles.eotiles import parse_to_list
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id
from eotile.eotiles.utils import build_logger, input_matcher, treat_eotiles


def main(
    input_arg,
    logger_file=None,
    no_l8=False,
    no_s2=False,
    dem=False,
    srtm5x5=False,
    location_type=None,
    min_overlap=None,
    epsg=None,
    threshold=None,
    verbose=None,
    overlap=False,
):
    """
    Main module of eotile
    Outputs a list of four lists containing tiles from respectively : Sentinel-2,
    Landscape 8, SRTM DEM and Copernicus

    :param input_arg:  Choose amongst : a file, a tile_id, a location, a wkt, a bbox
    :type input_arg: Str
    :param logger_file: [Optional, default = None] Redirect information
    from standard output to a file given by its path
    :type logger_file: Str
    :param epsg: [Optional, default = "4326"] Specify the epsg of the input
    :type epsg: Str
    :param min_overlap: [Optional, default = None] Minimum percentage of overlap to
    consider a tile (0 to 1)
    :type min_overlap: Str
    :param threshold: [Optional, default = None] For large polygons at high resolution,
    you might want to simplify them using a threshold (0 to 1)
    :type min_overlap: Str
    :param no_l8: [Optional, default = None] Do you want to ignore l8 tiles ?
    :type no_l8: Boolean
    :param no_s2: [Optional, default = None] Do you want to ignore s2 tiles ?
    :type no_s2: Boolean
    :param dem: [Optional, default = None] Do you want to use DEM tiles ?
    :type dem: Boolean
    :param srtm5x5: [Optional, default = None] Do you want to use specific SRTM 5x5 tiles ?
    :type srtm5x5: Boolean
    :param location_type: [Optional, default = None] Specify the value of the location
    (city, county, state, country)
    :type location_type: Str
    :param verbose: [Optional, default = None] Verbosity value, from 1 to 2
    :type verbose: Integer
    :param overlap: (Optional, default = False) Do you want to use the overlapping source file ?
    :type overlap: Boolean
    """
    if verbose is None:  # Default, no file
        log_level = logging.ERROR
    elif verbose == 1:  # Else, in a file
        log_level = logging.WARNING
    elif verbose == 2:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    dev_logger, user_logger = build_logger(log_level, logger_file)

    with open(
        pkg_resources.resource_filename(__name__, "config/data_path")
    ) as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = Path(
        pkg_resources.resource_filename(__name__, data_path.strip())
    )
    tile_list_s2, tile_list_l8, tile_list_dem, tile_list_srtm5x5 = [], [], [], []
    induced_type = input_matcher(input_arg)

    if induced_type == "tile_id":
        (
            tile_list_s2,
            tile_list_l8,
            tile_list_dem,
            tile_list_srtm5x5,
        ) = get_tiles_from_tile_id(
            parse_to_list(input_arg),
            aux_data_dirpath,
            no_l8,
            no_s2,
            dem,
            srtm5x5,
            min_overlap,
            overlap,
        )
    else:
        if not no_s2:
            # S2 Tiles
            if not overlap:
                filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"
            else:
                filename_tiles_s2 = aux_data_dirpath / "s2_with_overlap.gpkg"
            tile_list_s2 = treat_eotiles(
                induced_type,
                input_arg,
                "S2",
                dev_logger,
                epsg,
                filename_tiles_s2,
                min_overlap,
                location_type,
                threshold,
            )

        if not no_l8:
            # L8 Tiles
            filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
            tile_list_l8 = treat_eotiles(
                induced_type,
                input_arg,
                "L8",
                dev_logger,
                epsg,
                filename_tiles_l8,
                min_overlap,
                location_type,
                threshold,
            )

        if dem:
            # SRTM Tiles
            filename_tiles_dem = aux_data_dirpath / "DEM_Union.gpkg"
            tile_list_dem = treat_eotiles(
                induced_type,
                input_arg,
                "DEM",
                dev_logger,
                epsg,
                filename_tiles_dem,
                min_overlap,
                location_type,
                threshold,
            )

        if srtm5x5:
            # Copernicus Tiles
            filename_tiles_srtm5x5 = aux_data_dirpath / "srtm5x5_tiles.gpkg"
            tile_list_srtm5x5 = treat_eotiles(
                induced_type,
                input_arg,
                "SRTM 5x5",
                dev_logger,
                epsg,
                filename_tiles_srtm5x5,
                min_overlap,
                location_type,
                threshold,
            )
    #
    # Outputting the result
    return [tile_list_s2, tile_list_l8, tile_list_dem, tile_list_srtm5x5]


def quick_search(
    input_arg,
    search_type,
    tile_source,
    location_type=None,
    min_overlap=None,
    epsg=None,
    threshold=None,
    overlap=False,
):

    """
    Advanced QuickSearch for EOTiles
    Outputs a single DataFrame

    :param input_arg:  Choose amongst : a file, a tile_id, a location, a wkt, a bbox
    :type input_arg: Str
    :param search_type: Precise the input_arg type : "tile_id", "wkt", "location", "bbox", "file"
    :type search_type: Str
    :param tile_source: Precise the requested output type : "S2", "L8", "SRTM", "Copernicus"
    :type tile_source: Str
    :param epsg: [Optional, default = "4326"] Specify the epsg of the input
    :type epsg: Str
    :param min_overlap: [Optional, default = None] Minimum percentage of overlap to
    consider a tile (0 to 1)
    :type min_overlap: Str
    :param threshold: [Optional, default = None] For large polygons at high resolution,
    you might want to simplify them using a threshold (0 to 1)
    :type min_overlap: Str
    :param location_type: [Optional, default = None] Specify the value of the location
    (city, county, state, country)
    :type location_type: Str
    :param overlap: (Optional, default = False) Do you want to use the overlapping source file ?
    :type overlap: Boolean
    """
    with open(
        pkg_resources.resource_filename(__name__, "config/data_path")
    ) as conf_file:
        data_path = conf_file.readline()
    aux_data_dirpath = Path(
        pkg_resources.resource_filename(__name__, data_path.strip())
    )
    filenames = []
    if not overlap:
        filenames.append(aux_data_dirpath / "s2_no_overlap.gpkg")
    else:
        filenames.append(aux_data_dirpath / "s2_with_overlap.gpkg")
    filenames.append(aux_data_dirpath / "l8_tiles.gpkg")
    filenames.append(aux_data_dirpath / "DEM_Union.gpkg")
    filenames.append(aux_data_dirpath / "srtm5x5_tiles.gpkg")
    positioning_dict = {"S2": 0, "L8": 1, "DEM": 2, "SRTM 5x5": 3}
    if search_type == "tile_id":
        ret = get_tiles_from_tile_id(
            parse_to_list(input_arg),
            aux_data_dirpath,
            False,
            False,
            True,  # WHAT WHY ?...
            True,
            min_overlap,
            overlap,
        )
        return ret[positioning_dict[tile_source]]
    else:
        dev_logger, user_logger = build_logger(logging.ERROR, None)
        return treat_eotiles(
            search_type,
            input_arg,
            tile_source,
            dev_logger,
            epsg,
            filenames[positioning_dict[tile_source]],
            min_overlap,
            location_type,
            threshold,
        )
