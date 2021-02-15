# -*- coding: utf-8 -*-
"""
EO tile

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import os
import sys
import xml.etree.ElementTree as ET

from osgeo import ogr, osr


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

    def write_tile_bb(self, filename):
        """ Write the Bounding Box of a tile"""
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.CreateDataSource(filename)
        if os.path.exists(filename):
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
        print("== Tile L8 ==")
        EOTile.display(self)

    @classmethod
    def from_tile_id(cls, tile_id, tile_grid_filepath):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # Open the tile list file
        dataSource_tile_list = driver.Open(tile_grid_filepath, 0)
        # Check to see if shapefile is found.
        if dataSource_tile_list is None:
            print("ERROR: Could not open {}".format(tile_grid_filepath))
            return None
        layer_tile_list = dataSource_tile_list.GetLayer()
        layer_tile_list.SetAttributeFilter("WRSPR = {}".format(tile_id))

        for feature in layer_tile_list:
            print("{}, {}".format(feature.GetField("PATH"), feature.GetField("ROW")))
            # print(feature.GetGeometryRef().Clone())
            print(feature.GetGeometryRef().Centroid())

        return cls()

    @classmethod
    def from_poly_wkt(cls, poly_wkt, tile_grid_filepath):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # Open the tile list file
        dataSource_tile_list = driver.Open(tile_grid_filepath, 0)
        # Check to see if shapefile is found.
        if dataSource_tile_list is None:
            print("ERROR: Could not open {}".format(tile_grid_filepath))
            return None
        layer_tile_list = dataSource_tile_list.GetLayer()

        layer_tile_list.SetSpatialFilter(ogr.CreateGeometryFromWkt(poly_wkt))

        for feature in layer_tile_list:
            print("{}, {}".format(feature.GetField("PATH"), feature.GetField("ROW")))


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
        print("== S2 Tile ==")
        EOTile.display(self)
        print(self.BB)
        print(self.UL)
        print(self.SRS)
        print(self.NRows)
        print(self.NCols)
        print(self.poly)

    def create_poly_bb(self):
        """ Create the OGR Polygon from the list of BB corner """
        # Create ring
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(float(self.BB[1]), float(self.BB[0]))
        ring.AddPoint(float(self.BB[3]), float(self.BB[2]))
        ring.AddPoint(float(self.BB[5]), float(self.BB[4]))
        ring.AddPoint(float(self.BB[7]), float(self.BB[6]))
        ring.AddPoint(float(self.BB[1]), float(self.BB[0]))

        # Create polygon
        self.polyBB = ogr.Geometry(ogr.wkbPolygon)
        self.polyBB.AddGeometry(ring)

    def create_poly_tile(self):
        """ Create the OGR Polygon from the list of corners """
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
        if os.path.exists(filename):
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

    @classmethod
    def from_tile_id(cls, tile_id, tile_grid_filepath):
        # Open the tiles list file
        tree = ET.parse(tile_grid_filepath)
        root = tree.getroot()

        for tile_elt in root.findall("./DATA/REPRESENTATION_CODE_LIST/TILE_LIST/TILE"):
            if tile_elt.find("TILE_IDENTIFIER").text == tile_id:
                tile = cls()
                tile.ID = tile_elt.find("TILE_IDENTIFIER").text
                tile.SRS = tile_elt.find("HORIZONTAL_CS_CODE").text
                tile.UL[0] = int(tile_elt.find("ULX").text)
                tile.UL[1] = int(tile_elt.find("ULY").text)
                tile_bb = tile_elt.find("B_BOX").text
                tile.BB = tile_bb.split(" ")
                # Create the polygon
                tile.create_poly_bb()
                print(tile.polyBB)
                print(tile.polyBB.Centroid())

                return tile

        return None
