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
EO tile

:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
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
    parser.add_argument(
        "-no_l8", action="store_true", help="output L8 tiles"
    )
    parser.add_argument(
        "-no_s2", action="store_true", help="Disable S2 tiles"
    )
    parser.add_argument("-srtm", action="store_true", help="Use SRTM tiles as well")
    parser.add_argument("-cop", action="store_true", help="Use Copernicus tiles as well")
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
        help="Output the location of the centroid of matching tiles " "on standard output",
    )
    parser.add_argument(
        "-s2_overlap",
        action="store_true",
        help="Do you want to have overlaps on S2 tiles ?",
    )

    parser.add_argument("-v", "--verbose", action="count", help="Increase output verbosity")

    parser.add_argument("-logger_file", help="Redirect information from standard output to a file")

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


def main(arguments=None):
    """
    Command line interface to perform

    :param list arguments: list of arguments
    """
    arg_parser = build_parser()
    args = arg_parser.parse_args(args=arguments)

    [tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop] = eotile_module.main(
        args.input,
        args.logger_file,
        args.no_l8,
        args.no_s2,
        args.srtm,
        args.cop,
        args.location_type,
        args.min_overlap,
        args.epsg,
        args.threshold,
        args.verbose,
        args.s2_overlap,
    )
    tile_sources = ["S2", "L8", "SRTM", "Copernicus"]
    user_logger = logging.getLogger("user_logger")

    # Outputting the result
    tile_lists = [tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop]
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
                        output_path.with_name(output_path.stem + "_" + source +
                                              output_path.suffix),
                    )
    elif args.to_wkt:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                for elt in tile_list["geometry"]:
                    user_logger.info("%s Tile: %s", source, elt.wkt)
    elif args.to_bbox:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                for elt in tile_list["geometry"]:
                    user_logger.info("%s Tile Bounds: %s", source, str(elt.bounds))
    elif args.to_tile_id:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                for elt in tile_list["id"]:
                    user_logger.info("%s Tile id: %s", source, str(elt))
    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list["geometry"]:
                    centroid = list(list(elt.centroid.coords)[0])
                    centroid.reverse()
                    location = geolocator.reverse(centroid, language='en')
                    if location is not None:
                        user_logger.info(str(location))
    else:
        for i, tile_list in enumerate(tile_lists):
            source = tile_sources[i]
            if len(tile_list) > 0:
                for elt in tile_list[["id", "geometry"]].iterrows():
                    user_logger.info(
                        "[" + source + " tile]\n" + elt[1]["id"] + "\n" + elt[1]["geometry"].wkt
                    )
    # counts
    user_logger.info("--- Summary ---")
    for i, tile_list in enumerate(tile_lists):
        source = tile_sources[i]
        if len(tile_list) > 0:
            user_logger.info("- %s %s Tiles", len(tile_list), source)


if __name__ == "__main__":
    sys.exit(main())
