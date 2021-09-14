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

import argparse
import logging
import sys
from pathlib import Path

from geopy.geocoders import Nominatim

from eotile import eotile_module
from eotile.eotiles.eotiles import write_tiles_bb


def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Choose amongst : a file, a tile_id, a location, a wkt, a bbox",
    )
    parser.add_argument("-epsg", help="Specify the epsg of the input")
    parser.add_argument("-no_l8", action="store_true", help="output L8 tiles")
    parser.add_argument("-no_s2", action="store_true", help="Disable S2 tiles")
    parser.add_argument("-dem", action="store_true", help='Use DEM 1" tiles as well')
    parser.add_argument(
        "-srtm5x5", action="store_true", help="Use specific srtm 5x5 tiles as well"
    )
    # Output arguments

    parser.add_argument("-to_file", help="Write tiles to a file")
    parser.add_argument(
        "-to_wkt",
        action="store_true",
        help="Output the geometry of matching tiles with wkt format on standard output",
    )
    parser.add_argument(
        "-to_bbox",
        action="store_true",
        help="Output the bounding box of matching tiles on standard output",
    )
    parser.add_argument(
        "-to_tile_id",
        action="store_true",
        help="Output the id(s) of matching tiles on standard output",
    )
    parser.add_argument(
        "-to_location",
        action="store_true",
        help="Output the location of the centroid of matching tiles "
        "on standard output",
    )
    parser.add_argument(
        "-s2_overlap",
        action="store_true",
        help="Do you want to have overlaps on S2 tiles ?",
    )

    parser.add_argument(
        "-v", "--verbose", action="count", help="Increase output verbosity"
    )

    parser.add_argument(
        "-logger_file", help="Redirect information from standard output to a file"
    )

    parser.add_argument(
        "-location_type",
        help="If needed, specify the location type that is requested (city, county, state, country)",
    )

    parser.add_argument(
        "-threshold",
        help="For large polygons at high resolution, you might want to simplify them using a threshold"
        "(0 to 1)",
    )

    parser.add_argument(
        "-min_overlap",
        help="Minimum percentage of overlap to consider a tile (0 to 1)",
    )

    return parser


def build_output(source, tile_list, user_logger, message, args):
    """
    Sub-function of the main
    Formats an output depending on a specified message & arguments over a dataframe pandas of tiles.
    :param source: Type of the source (DEM, S2, L8)
    :type source: str
    :param user_logger: LOGGER to log the message to
    :type user_logger: logging.LOGGER
    :param tile_list: pandas dataframe of the tiles to format
    :type tile_list: pandas DataFrame
    :param message: The message to format
    :type message: str
    :param args: fields to look in
    :type args: list
    """
    if source != "DEM":
        interesting_columns = []
        for elt in args:
            if elt == "bounds":
                interesting_columns.append("geometry")
            else:
                interesting_columns.append(elt)
        for elt in tile_list[interesting_columns].iterrows():
            arguments = []
            for arg in args:
                if arg == "geometry":
                    arguments.append(elt[1]["geometry"].wkt)
                elif arg == "bounds":
                    arguments.append(elt[1]["geometry"].bounds)
                else:
                    arguments.append(str(elt[1][arg]))
            user_logger.info(message.format(source, *arguments))
    else:
        interesting_columns = ["EXIST_SRTM", "EXIST_COP30", "EXIST_COP90"]
        for elt in args:
            if elt == "bounds":
                interesting_columns.append("geometry")
            else:
                interesting_columns.append(elt)
        for elt in tile_list[interesting_columns].iterrows():
            availability = []
            if elt[1]["EXIST_SRTM"]:
                availability.append("SRTM")
            if elt[1]["EXIST_COP30"]:
                availability.append("Copernicus 30")
            if elt[1]["EXIST_COP90"]:
                availability.append("Copernicus 90")
            arguments = []
            for arg in args:
                if arg == "geometry":
                    arguments.append(elt[1]["geometry"].wkt)
                elif arg == "bounds":
                    arguments.append(elt[1]["geometry"].bounds)
                else:
                    arguments.append(str(elt[1][arg]))
            user_logger.info(message.format(", ".join(availability), *arguments))


def main(arguments=None):
    """
    Command line interface to perform

    :param list arguments: list of arguments
    """
    arg_parser = build_parser()
    args = arg_parser.parse_args(args=arguments)
    [tile_list_s2, tile_list_l8, tile_list_dem, tile_list_srtm5x5] = eotile_module.main(
        args.input,
        args.logger_file,
        args.no_l8,
        args.no_s2,
        args.dem,
        args.srtm5x5,
        args.location_type,
        args.min_overlap,
        args.epsg,
        args.threshold,
        args.verbose,
        args.s2_overlap,
    )
    tile_sources = ["S2", "L8", "DEM", "SRTM 5x5"]
    user_logger = logging.getLogger("user_logger")

    # Outputting the result
    tile_lists = [tile_list_s2, tile_list_l8, tile_list_dem, tile_list_srtm5x5]
    if args.to_file is not None:
        output_path = Path(args.to_file)
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                if output_path.suffix == ".gpkg":
                    # Using layers method to combine sources if geopackage
                    write_tiles_bb(tile_list, output_path, source=source)
                else:
                    # Else, we split into several files
                    write_tiles_bb(
                        tile_list,
                        output_path.with_name(
                            output_path.stem + "_" + source + output_path.suffix
                        ),
                    )
    elif args.to_wkt:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                build_output(
                    source, tile_list, user_logger, "[{}] Tile: {}", ["geometry"]
                )

    elif args.to_bbox:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                build_output(
                    source, tile_list, user_logger, "[{}] Tile Bounds: {}", ["bounds"]
                )

    elif args.to_tile_id:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                build_output(source, tile_list, user_logger, "[{}] Tile id: {}", ["id"])

    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list["geometry"]:
                    centroid = list(list(elt.centroid.coords)[0])
                    centroid.reverse()
                    location = geolocator.reverse(centroid, language="en")
                    if location is not None:
                        user_logger.info(str(location))
    else:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                build_output(
                    source,
                    tile_list,
                    user_logger,
                    "[{} tile]\n {}\n {}",
                    ["id", "geometry"],
                )

    # counts
    user_logger.info("--- Summary ---")
    for i, tile_list in enumerate(tile_lists):
        source = tile_sources[i]
        if len(tile_list) > 0:
            user_logger.info("- %s %s Tiles", len(tile_list), source)


if __name__ == "__main__":
    sys.exit(main())
