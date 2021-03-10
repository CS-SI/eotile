# -*- coding: utf-8 -*-
"""
EO tile

:author: msavinaud; mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from shapely.geometry import Polygon, MultiPolygon

LOGGER = logging.getLogger("dev_logger")


class EOTile:
    """Class which represent a tile """

    def __init__(self):
        """ Constructor """

        self.ID = None
        self.polyBB = None
        self.source = None

    def __str__(self):
        """ Display the content of a tile"""
        string_representation = f"== Tile {self.source} ==\n"
        string_representation += str(self.ID) + "\n"
        string_representation += str(self.polyBB) + "\n"
        return string_representation

    def get_bb(self):
        """
        Returns the AABB (axis aligned bounding box) of a tile.

        """
        return self.polyBB.GetEnvelope()


class S2Tile(EOTile):
    """Class which represent a S2 tile read from Tile_Part file"""

    def __init__(self):
        EOTile.__init__(self)
        self.source = "S2"
        self.BB = [0, 0, 0, 0, 0, 0, 0, 0]
        self.poly = None
        self.UL = [0, 0]
        self.SRS = None
        self.NRows = []
        self.NCols = []

    def __str__(self):
        """ Display the content of tile"""
        string_representation = super().__str__()
        string_representation += str(self.BB) + "\n"
        string_representation += str(self.UL) + "\n"
        string_representation += str(self.SRS) + "\n"
        string_representation += str(self.NRows) + "\n"
        string_representation += str(self.NCols) + "\n"
        # string_representation += str(self.poly) + "\n"
        return string_representation

    def create_poly_bb(self):
        """ Create the Shapely Polygon from the list of BB corner """
        indices = [[1, 0], [3, 2], [5, 4], [7, 6]]
        # Create polygon
        self.polyBB = Polygon([[float(self.BB[ind[0]]), float(self.BB[ind[1]])] for ind in indices])

    def compute_datetime_point(self, east_pt, west_pt):
        """
        Computes the latitude of the point on the datetime line from two points on each side of that line

        :param east_pt: Point of the east part of the line
        :param west_pt:  Point of the west part of the line
        """
        lat = 1  # index of latitudes
        long = 1 - lat
        c1_den = -float(self.BB[east_pt[long]]) + float(self.BB[west_pt[long]]) + 360
        c1_num = 180 - float(self.BB[east_pt[long]])
        coeff1_lat = float(self.BB[west_pt[lat]]) - float(self.BB[east_pt[lat]])
        return float(self.BB[east_pt[lat]]) + c1_num / c1_den * coeff1_lat

    def datetime_cutter(self):
        """ Create the Shapely Polygon from the list of BB corner in the case where it crosses the datetime_line"""
        indices = [[1, 0], [3, 2], [5, 4], [7, 6]]
        # compute latitude of cutting points
        [a_point, b_point, c_point, d_point] = indices
        if (abs(float(self.BB[1]) - float(self.BB[3])) > 355.0) and (
            abs(float(self.BB[5]) - float(self.BB[7])) > 355.0
        ):  # Case where two segments are of each side of the datetime line
            c1_lat = self.compute_datetime_point(a_point, b_point)
            c2_lat = self.compute_datetime_point(d_point, c_point)
            # Create east polygon
            east_part = Polygon(
                (
                    [
                        [float(self.BB[indices[0][0]]), float(self.BB[indices[0][1]])],
                        [180, c1_lat],
                        [180, c2_lat],
                        [float(self.BB[indices[3][0]]), float(self.BB[indices[3][1]])],
                    ]
                )
            )
            # Create west polygon
            west_part = Polygon(
                (
                    [
                        [-180, c1_lat],
                        [float(self.BB[indices[1][0]]), float(self.BB[indices[1][1]])],
                        [float(self.BB[indices[2][0]]), float(self.BB[indices[2][1]])],
                        [-180, c2_lat],
                    ]
                )
            )
        elif (abs(float(self.BB[1]) - float(self.BB[3])) > 355.0) and not (
            abs(float(self.BB[5]) - float(self.BB[7])) > 355.0
        ):  # Case where only top line is crossed
            # Case 1a
            #   _
            # /_/
            if float(self.BB[5]) > 0 and not float(self.BB[3]) > 0:
                c1_lat = self.compute_datetime_point(a_point, b_point)
                c2_lat = self.compute_datetime_point(c_point, b_point)
                east_part = Polygon(
                    (
                        [
                            [
                                float(self.BB[indices[0][0]]),
                                float(self.BB[indices[0][1]]),
                            ],
                            [180, c1_lat],
                            [180, c2_lat],
                            [
                                float(self.BB[indices[2][0]]),
                                float(self.BB[indices[2][1]]),
                            ],
                            [
                                float(self.BB[indices[3][0]]),
                                float(self.BB[indices[3][1]]),
                            ],
                        ]
                    )
                )
                # Create west polygon
                west_part = Polygon(
                    (
                        [
                            [-180, c1_lat],
                            [
                                float(self.BB[indices[1][0]]),
                                float(self.BB[indices[1][1]]),
                            ],
                            [-180, c2_lat],
                        ]
                    )
                )
            # Case 2a
            #  _
            #  \_\
            elif float(self.BB[1]) > 0 and not float(self.BB[7]) > 0:
                c1_lat = self.compute_datetime_point(a_point, b_point)
                c2_lat = self.compute_datetime_point(a_point, d_point)
                east_part = Polygon(
                    (
                        [
                            [
                                float(self.BB[indices[0][0]]),
                                float(self.BB[indices[0][1]]),
                            ],
                            [180, c1_lat],
                            [180, c2_lat],
                        ]
                    )
                )
                # Create west polygon
                west_part = Polygon(
                    (
                        [
                            [-180, c1_lat],
                            [
                                float(self.BB[indices[1][0]]),
                                float(self.BB[indices[1][1]]),
                            ],
                            [
                                float(self.BB[indices[2][0]]),
                                float(self.BB[indices[2][1]]),
                            ],
                            [
                                float(self.BB[indices[3][0]]),
                                float(self.BB[indices[3][1]]),
                            ],
                            [-180, c2_lat],
                        ]
                    )
                )
            else:
                LOGGER.error("Unrecognized crossing BBOX : ", self.BB)

        elif not (abs(float(self.BB[1]) - float(self.BB[3])) > 355.0) and (
            abs(float(self.BB[5]) - float(self.BB[7])) > 355.0
        ):  # Case where only bottom line is crossed
            # Case 1b
            #   _
            # /_/
            if float(self.BB[7]) > 0 and not float(self.BB[1]) > 0:
                c1_lat = self.compute_datetime_point(d_point, a_point)
                c2_lat = self.compute_datetime_point(d_point, c_point)
                east_part = Polygon(
                    (
                        [
                            [
                                float(self.BB[indices[3][0]]),
                                float(self.BB[indices[3][1]]),
                            ],
                            [180, c1_lat],
                            [180, c2_lat],
                        ]
                    )
                )
                # Create west polygon
                west_part = Polygon(
                    (
                        [
                            [-180, c1_lat],
                            [
                                float(self.BB[indices[0][0]]),
                                float(self.BB[indices[0][1]]),
                            ],
                            [
                                float(self.BB[indices[1][0]]),
                                float(self.BB[indices[1][1]]),
                            ],
                            [
                                float(self.BB[indices[2][0]]),
                                float(self.BB[indices[2][1]]),
                            ],
                            [-180, c2_lat],
                        ]
                    )
                )
            # Case 2b
            #  _
            #  \_\
            elif float(self.BB[3]) > 0 and not float(self.BB[5]) > 0:
                c1_lat = self.compute_datetime_point(b_point, c_point)
                c2_lat = self.compute_datetime_point(d_point, c_point)
                east_part = Polygon(
                    (
                        [
                            [
                                float(self.BB[indices[0][0]]),
                                float(self.BB[indices[0][1]]),
                            ],
                            [
                                float(self.BB[indices[1][0]]),
                                float(self.BB[indices[1][1]]),
                            ],
                            [180, c1_lat],
                            [180, c2_lat],
                            [
                                float(self.BB[indices[3][0]]),
                                float(self.BB[indices[3][1]]),
                            ],
                        ]
                    )
                )
                # Create west polygon
                west_part = Polygon(
                    (
                        [
                            [-180, c1_lat],
                            [
                                float(self.BB[indices[2][0]]),
                                float(self.BB[indices[2][1]]),
                            ],
                            [-180, c2_lat],
                        ]
                    )
                )
            else:
                LOGGER.error("Unrecognized crossing BBOX : ", self.BB)
        else:
            LOGGER.error("Unrecognized crossing BBOX : ", self.BB)

        self.polyBB = MultiPolygon([east_part, west_part])
