# -*- coding: utf-8 -*-
"""
EO tile

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import pathlib

from lxml import etree as ET
from osgeo import ogr, osr
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

    def write_tile_bb(self, filename):
        """ Write the Bounding Box of a tile"""
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.CreateDataSource(filename)
        if pathlib.Path(filename).exists():
            driver.DeleteDataSource(filename)

        # create the spatial reference for the bounding box, WGS84
        srs_bb = osr.SpatialReference()
        srs_bb.ImportFromEPSG(4326)
        # create the layer
        layer_bb = data_source.CreateLayer("bb", srs_bb, ogr.wkbPolygon)

        # Add the fields
        field_name = ogr.FieldDefn("TileID", ogr.OFTString)
        field_name.SetWidth(10)
        layer_bb.CreateField(field_name)

        feature = ogr.Feature(layer_bb.GetLayerDefn())
        feature.SetField("TileID", self.ID)
        feature.SetGeometry(self.polyBB)
        layer_bb.CreateFeature(feature)
        feature.Destroy()

        data_source.Destroy()


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
        """ Create the OGR Polygon from the list of BB corner """
        indices = [[1, 0], [3, 2], [5, 4], [7, 6]]
        # Create polygon
        self.polyBB = Polygon([[float(self.BB[ind[0]]), float(self.BB[ind[1]])] for ind in indices])


    def create_poly_tile(self):
        """ Create the OGR Polygon from the list of corners """
        # TODO : check that part for epsg
        # Compute tile corner
        tile_urx = self.UL[0] + self.NCols[0] * 10
        tile_ury = self.UL[1]
        tile_llx = self.UL[0]
        tile_lly = self.UL[1] + self.NRows[0] * 10
        tile_lrx = self.UL[0] + self.NCols[0] * 10
        tile_lry = self.UL[1] + self.NRows[0] * 10

        # Create ring
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(self.UL[0], self.UL[1])
        ring.AddPoint(tile_urx, tile_ury)
        ring.AddPoint(tile_lrx, tile_lry)
        ring.AddPoint(tile_llx, tile_lly)
        ring.AddPoint(self.UL[0], self.UL[1])

        # Create polygon
        self.poly = ogr.Geometry(ogr.wkbPolygon)
        self.poly.AddGeometry(ring)

    def write_tile(self, filename):
        """ Write the OGR polygon of a S2 tile"""
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.CreateDataSource(filename)
        if pathlib.Path(filename).exists():
            driver.DeleteDataSource(filename)

        # create the spatial reference for the tile
        srs_tile_str = self.SRS.split(":")
        srs_tile = osr.SpatialReference()
        srs_tile.ImportFromEPSG(int(srs_tile_str[1]))
        # create the layer
        layer_tile = data_source.CreateLayer("tile", srs_tile, ogr.wkbPolygon)

        # Add the fields
        field_name = ogr.FieldDefn("TileID", ogr.OFTString)
        field_name.SetWidth(10)
        layer_tile.CreateField(field_name)

        feature = ogr.Feature(layer_tile.GetLayerDefn())
        feature.SetField("TileID", self.ID)
        feature.SetGeometry(self.poly)
        layer_tile.CreateFeature(feature)
        feature.Destroy()

        data_source.Destroy()