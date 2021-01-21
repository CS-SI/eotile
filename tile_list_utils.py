# -*- coding: utf-8 -*-
"""
tile list utilities

:author: msavinaud
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import os
import copy
import xml.etree.ElementTree as ET

from osgeo import ogr, osr
import numpy

from eotile import *


### ------------------------------------------------------------------------- ###
### Tile list functions ###         
        
def write_tiles_bb(tile_list, filename, sensor='S2'):
    """ Write the content of a tile list """
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

    
    for tile in tile_list:
        feature = ogr.Feature(layer_bb.GetLayerDefn())
        feature.SetField("TileID",tile.ID)    
        feature.SetGeometry(tile.polyBB)
        layer_bb.CreateFeature(feature)
        feature.Destroy()
       
    data_source.Destroy()        

    
def create_tiles_list_S2(filename_tiles_list, filename_aoi=None):
    """ Create the S2 tile list according to an aoi """ 
    #Open the tiles list file
    tree = ET.parse(filename_tiles_list)
    root = tree.getroot()
    
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    #Open the AOI file
    dataSource_aoi = driver.Open(filename_aoi, 0)
    # Check to see if shapefile is found.
    if dataSource_aoi is None:
        print('ERROR: Could not open {}'.format(filename_aoi))
        return None
    
    layer_aoi = dataSource_aoi.GetLayer()
    featureCount = layer_aoi.GetFeatureCount()
    if featureCount != 1:
        print("ERROR: Number of features in {}: {}".format(os.path.basename(filename_aoi),featureCount))
        return None

    # Get the first feature
    feature_aoi= layer_aoi.GetNextFeature()
    
    tile_list=[]
    tile_dateline = 0
    for tile_elt in root.findall("./DATA/REPRESENTATION_CODE_LIST/TILE_LIST/TILE"):
        tile = S2Tile()
        tile.ID = tile_elt.find('TILE_IDENTIFIER').text
        tile.SRS = tile_elt.find('HORIZONTAL_CS_CODE').text
        tile.UL[0] = int(tile_elt.find('ULX').text)
        tile.UL[1] = int(tile_elt.find('ULY').text)
        tile_bb = tile_elt.find('B_BOX').text
        tile.BB = tile_bb.split(' ')
        
        # TODO: Manage properly the case where the polygon cut the dateline (long +/-180�)
        #       take a look to the FixPolygonCoordinatesAtDateLine method into 
        #       gdal/ogr/ogrgeometryfactory.cpp
        if (abs(float(tile.BB[1]) - float(tile.BB[3])) > 355.) or (abs(float(tile.BB[5]) - float(tile.BB[7])) > 355.):
            tile_dateline += 1 
            continue
        
        # Create the polygon
        tile.create_poly_bb()
        
        # Intersect with the AOI  
        if tile.polyBB.Intersects(feature_aoi.GetGeometryRef()):

            for tile_elt_size in tile_elt.findall("./TILE_SIZE_LIST/TILE_SIZE"):
                tile.NRows.append(int(tile_elt_size.find('NROWS').text))
                tile.NCols.append(int(tile_elt_size.find('NCOLS').text))

            
            tile.create_poly_tile()
            tile_list.append(tile)
    
    print("WARNING: some of tiles are excluded due to the dateline issue {}.".format(tile_dateline))
    return tile_list


    
def create_tiles_list_L8(filename_tiles_list, filename_aoi=None):
    """ Create the L8 tile list according to an aoi """     
    driver = ogr.GetDriverByName("ESRI Shapefile")
    #Open the tile list file
    dataSource_tile_list = driver.Open(filename_tiles_list, 0)
    # Check to see if shapefile is found.
    if dataSource_tile_list is None:
        print('ERROR: Could not open {}'.format(filename_tiles_list))
        return None
    
    layer_tile_list = dataSource_tile_list.GetLayer()
    featureCount = layer_tile_list.GetFeatureCount()
    print("Number of features in {}: {}".format(os.path.basename(filename_tiles_list),featureCount))    
    
    #Open the AOI file
    dataSource_aoi = driver.Open(filename_aoi, 0)
    # Check to see if shapefile is found.
    if dataSource_aoi is None:
        print('ERROR: Could not open {}'.format(filename_aoi))
        return None


    layer_aoi = dataSource_aoi.GetLayer()
    featureCount = layer_aoi.GetFeatureCount()
    if featureCount != 1:
        print("ERROR: Number of features in {}: {}".format(os.path.basename(filename_aoi),featureCount))
        return None

    # Get the first feature
    feature_aoi= layer_aoi.GetNextFeature()
        
    tile_list=[]
    
    layer_tile_list.SetSpatialFilter(feature_aoi.GetGeometryRef())
    
    for feature_tile_list in layer_tile_list:
        tile = L8Tile()
        
        tile.ID =  feature_tile_list.GetField("PR")
        tile.polyBB = feature_tile_list.GetGeometryRef().Clone()
            
        tile_list.append(tile)
            
    return tile_list        

def get_tile(tile_list, tile_id):
    """ Get a tile from a tile list according to a tile ID  """ 
    if (len(tile_list) == 0):
        return None
    
    i=-1
    while tile_list[i+1].ID != tile_id:
        i+=1
    
    if (i != len(tile_list)):
        return tile_list[i]
    else:
        return None

  
def read_tile_list_from_file(filename_tiles):
    """ Read a tile list from a file previously created"""
    driver = ogr.GetDriverByName("ESRI Shapefile")
    #Open the tile list file
    dataSource_tile_list = driver.Open(filename_tiles, 0)
    # Check to see if shapefile is found.
    if dataSource_tile_list is None:
        print('ERROR: Could not open {}'.format(filename_tiles))
        return None
    
    layer_tile_list = dataSource_tile_list.GetLayer()
    featureCount = layer_tile_list.GetFeatureCount()
    print("Number of features in {}: {}".format(os.path.basename(filename_tiles),featureCount))
    
    tile_list = []
    for feature_tile_list in layer_tile_list:
        tile = EOTile()
        tile.ID =  feature_tile_list.GetField("TileID")
        tile.polyBB = feature_tile_list.GetGeometryRef().Clone()
        tile_list.append(tile)
        
    return tile_list
    