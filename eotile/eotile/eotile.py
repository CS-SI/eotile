# -*- coding: utf-8 -*-
"""
EO tile

:author: msavinaud; mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging

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
