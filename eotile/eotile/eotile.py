# -*- coding: utf-8 -*-
"""
EO tile

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
from lxml import etree as ET
from shapely.geometry import Polygon

LOGGER = logging.getLogger(__name__)


class EOTile:
    """Class which represent a tile """

    def __init__(self):
        """ Constructor """

        self.ID = None
        self.polyBB = None

    def display(self):
        """ Display the content of a tile"""
        print(self.ID)
        print(self.polyBB)

    def get_bb(self):
        """
        Returns the AABB (axis aligned bounding box) of a tile.

        """
        return self.polyBB.GetEnvelope()

class L8Tile(EOTile):
    """ Class which represent a L8 tile """

    def __init__(self):
        """ Constructor """
        EOTile.__init__(self)

    def display(self):
        """ Display the content of a L8 tile"""
        LOGGER.info("== Tile L8 ==")
        EOTile.display(self)



class S2Tile(EOTile):
    """Class which represent a S2 tile read from Tile_Part file"""

    def __init__(self):
        EOTile.__init__(self)
        self.BB = [0, 0, 0, 0, 0, 0, 0, 0]
        self.poly = None
        self.UL = [0, 0]
        self.SRS = None
        self.NRows = []
        self.NCols = []

    def display(self):
        """ Display the content of tile"""
        LOGGER.info("== S2 Tile ==")
        EOTile.display(self)
        print(self.BB)
        print(self.UL)
        print(self.SRS)
        print(self.NRows)
        print(self.NCols)
        print(self.poly)

    def create_poly_bb(self):
        """ Create the Shapely Polygon from the list of BB corner """
        indices = [[1, 0], [3, 2], [5, 4], [7, 6]]
        # Create polygon
        self.polyBB = Polygon([[float(self.BB[ind[0]]), float(self.BB[ind[1]])] for ind in indices])