# -*- coding: utf-8 -*-
"""
EO tile

:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

import pkg_resources
import requests
from geopy.geocoders import Nominatim
from shapely.geometry import shape

from eotile.eotiles.eotiles import (
    bbox_to_wkt,
    create_tiles_list_eo,
    create_tiles_list_eo_from_geometry,
    create_tiles_list_s2,
    create_tiles_list_s2_from_geometry,
    geom_to_eo_tiles,
    geom_to_s2_tiles,
    write_tiles_bb,
)
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id


def build_logger(level, user_file_name=None):
    # Creating DEV logger
    dev_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    dev_handler = logging.FileHandler("dev_log.log")
    dev_handler.setFormatter(dev_formatter)

    dev_logger = logging.getLogger("dev_logger")
    dev_logger.setLevel(level)
    dev_logger.addHandler(dev_handler)

    # Creating User logger
    user_formatter = logging.Formatter("%(message)s")

    if user_file_name is not None:
        user_handler = logging.FileHandler(user_file_name)
    else:
        user_handler = logging.StreamHandler()
    user_handler.setFormatter(user_formatter)

    user_logger = logging.getLogger("user_logger")
    user_logger.setLevel(logging.INFO)
    user_logger.addHandler(user_handler)

    return dev_logger, user_logger


# noinspection Mypy
def input_matcher(input_value: str) -> str:
    """
    Induces the type of the input from the user input

    :param input_value: input provided by user of the cli
    :return: type of the input: wkt, bbox, tile_id, file, location
    :rtype: str
    :raises ValueError: when the input value cannot be parsed
    """
    poly_pattern = "(POLYGON|Polygon|MULTIPOLYGON|Multipolygon)(.*?)"

    bbox_pattern = "(.*?)(([0-9]|.|-|,|'| )*,).(.*?)"

    tile_id_pattern = "(([0-9]){6}|([0-9]){2}([A-Z]){3}|(N|S)([0-9]){2}(E|W)([0-9]){3})"

    poly_reg = re.compile(poly_pattern)
    bbox_reg = re.compile(bbox_pattern)
    tile_id_reg = re.compile(tile_id_pattern)

    if (
        poly_reg.match(input_value)
        and poly_reg.match(input_value).string == input_value
    ):
        return "wkt"

    if (
        bbox_reg.match(input_value)
        and bbox_reg.match(input_value).string == input_value
    ):
        return "bbox"

    if (
        tile_id_reg.match(input_value)
        and tile_id_reg.match(input_value).string == input_value
    ):
        return "tile_id"

    if Path(input_value).exists():
        return "file"

    geolocator = Nominatim(user_agent="eotile")
    location = geolocator.geocode(input_value)
    if location is not None:
        location_type = location.raw["type"]
        if location_type == "administrative":
            return "location"
        raise ValueError(
            "This location is has no administrative border: "
            + f"{input_value}, type= {location_type}"
        )

    raise ValueError(f"Cannot parse this input: {input_value}")


def build_parser():
    """Creates a parser suitable for parsing a command line invoking this program.

    :return: An parser.
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Choose amongst : file, tile_id, location, wkt, bbox. Then specify the argument",
    )
    parser.add_argument("-epsg", help="Specify the epsg of the input")
    parser.add_argument(
        "-s2_only", action="store_true", help="output S2 tiles which intersect the aoi"
    )
    parser.add_argument(
        "-l8_only", action="store_true", help="output L8 tiles which intersect the aoi"
    )
    parser.add_argument("-srtm", action="store_true", help="Use SRTM tiles as well")
    parser.add_argument(
        "-cop", action="store_true", help="Use Copernicus tiles as well"
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
        help="Minimum percentage of overlap to consider a tile" "(0 to 1)",
    )

    return parser


def treat_eotiles(
    induced_type,
    input_arg,
    tile_type,
    dev_logger,
    epsg,
    filename_tiles,
    min_overlap,
    location_type,
    threshold,
):
    """
    Treats Tiles that can be loaded from a standard geography file
    """
    if induced_type == "wkt":
        wkt = input_arg
        tile_list = geom_to_eo_tiles(wkt, epsg, filename_tiles, tile_type, min_overlap)
    elif induced_type == "location":
        geom = build_nominatim_request(location_type, input_arg, threshold)
        tile_list = create_tiles_list_eo_from_geometry(
            filename_tiles, geom, tile_type, min_overlap
        )
    elif induced_type == "bbox":
        wkt = bbox_to_wkt(input_arg)
        tile_list = geom_to_eo_tiles(wkt, epsg, filename_tiles, tile_type, min_overlap)
    elif induced_type == "file":
        aoi_filepath = Path(input_arg)
        tile_list = create_tiles_list_eo(
            filename_tiles, aoi_filepath, tile_type, min_overlap
        )
        dev_logger.info(
            "Nb of %s tiles which crossing the AOI: %s", tile_type, len(tile_list)
        )
    else:
        dev_logger.error("Unrecognized Option: %s", induced_type)
        tile_list = []

    return tile_list


def build_nominatim_request(location_type, input_arg, threshold):
    """
    Builds an http requests for nominatim, then runs it and outputs a geometry object
    """
    if location_type is not None:
        req = location_type
    else:
        req = "q"
    url = (
        f"https://nominatim.openstreetmap.org/search?{req}={input_arg}"
        f"&format=geojson&polygon_geojson=1&limit=1"
    )
    if threshold is not None:
        url += f"& polygon_threshold = {threshold}"
    data = requests.get(url)
    elt = data.json()
    geom = shape(elt["features"][0]["geometry"])
    return geom


def main(arguments=None):
    """
    Command line interface to perform

    :param list arguments: list of arguments
    """
    arg_parser = build_parser()
    args = arg_parser.parse_args(args=arguments)
    if args.verbose is None:  # Default
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    dev_logger, user_logger = build_logger(log_level, args.logger_file)

    with open(
        pkg_resources.resource_filename(__name__, "config/data_path")
    ) as conf_file:
        data_path = conf_file.readline()

    aux_data_dirpath = Path(
        pkg_resources.resource_filename(__name__, data_path.strip())
    )
    tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop = [], [], [], []
    induced_type = input_matcher(args.input)

    if induced_type == "tile_id":
        (
            tile_list_s2,
            tile_list_l8,
            tile_list_srtm,
            tile_list_cop,
        ) = get_tiles_from_tile_id(
            args.input,
            aux_data_dirpath,
            args.s2_only,
            args.l8_only,
            args.srtm,
            args.cop,
            args.min_overlap,
        )

    else:
        if not args.l8_only:
            # S2 Tiles
            filename_tiles_s2 = (
                aux_data_dirpath
                / "S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            )
            if induced_type == "wkt":
                wkt = args.input
                tile_list_s2 = geom_to_s2_tiles(
                    wkt, args.epsg, filename_tiles_s2, args.min_overlap
                )
            elif induced_type == "location":
                geom = build_nominatim_request(
                    args.location_type, args.input, args.threshold
                )
                tile_list_s2 = create_tiles_list_s2_from_geometry(
                    filename_tiles_s2, geom, args.min_overlap
                )
            elif induced_type == "bbox":
                wkt = bbox_to_wkt(args.input)
                tile_list_s2 = geom_to_s2_tiles(
                    wkt, args.epsg, filename_tiles_s2, args.min_overlap
                )
            elif induced_type == "file":
                aoi_filepath = Path(args.input)
                tile_list_s2 = create_tiles_list_s2(
                    filename_tiles_s2, aoi_filepath, args.min_overlap
                )
                dev_logger.info(
                    "Nb of S2 tiles which crossing the AOI: %s", len(tile_list_s2)
                )
            else:
                dev_logger.error("Unrecognized Option: %s", induced_type)

        if not args.s2_only:
            # L8 Tiles
            filename_tiles_l8 = (
                aux_data_dirpath / "wrs2_descending" / "wrs2_descending.shp"
            )
            tile_list_l8 = treat_eotiles(
                induced_type,
                args.input,
                "L8",
                dev_logger,
                args.epsg,
                filename_tiles_l8,
                args.min_overlap,
                args.location_type,
                args.threshold,
            )

        if args.srtm:
            # SRTM Tiles
            filename_tiles_srtm = aux_data_dirpath / "srtm" / "srtm_grid_1deg.shp"
            tile_list_srtm = treat_eotiles(
                induced_type,
                args.input,
                "SRTM",
                dev_logger,
                args.epsg,
                filename_tiles_srtm,
                args.min_overlap,
                args.location_type,
                args.threshold,
            )

        if args.cop:
            # Copernicus Tiles
            filename_tiles_cop = aux_data_dirpath / "Copernicus" / "dem30mGrid.shp"
            tile_list_cop = treat_eotiles(
                induced_type,
                args.input,
                "Copernicus",
                dev_logger,
                args.epsg,
                filename_tiles_cop,
                args.min_overlap,
                args.location_type,
                args.threshold,
            )
    #
    # Outputting the result
    tile_lists = [tile_list_s2, tile_list_l8, tile_list_srtm, tile_list_cop]
    if args.to_file is not None:
        output_path = Path(args.to_file)
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                write_tiles_bb(
                    tile_list,
                    output_path.with_name(
                        output_path.stem
                        + "_"
                        + tile_list[0].source
                        + output_path.suffix
                    ),
                )
    elif args.to_wkt:
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list:
                    user_logger.info("%s Tile: %s", elt.source, elt.polyBB.wkt)
    elif args.to_bbox:
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list:
                    user_logger.info(
                        "%s Tile Bounds: %s", elt.source, str(elt.polyBB.bounds)
                    )
    elif args.to_tile_id:
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list:
                    user_logger.info("%s Tile id: %s", elt.source, str(elt.ID))
    elif args.to_location:
        geolocator = Nominatim(user_agent="EOTile")
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list:
                    centroid = list(list(elt.polyBB.centroid.coords)[0])
                    centroid.reverse()
                    location = geolocator.reverse(centroid)
                    if location is not None:
                        user_logger.info(str(location))
    else:
        for tile_list in tile_lists:
            if len(tile_list) > 0:
                for elt in tile_list:
                    user_logger.info(str(elt))
    # counts
    user_logger.info("--- Summary ---")
    for tile_list in tile_lists:
        if len(tile_list) > 0:
            user_logger.info("- %s %s Tiles", len(tile_list), tile_list[0].source)


if __name__ == "__main__":
    sys.exit(main())
