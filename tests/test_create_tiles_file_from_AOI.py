# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from eotile.utils.tile_list_utils import create_tiles_list_S2

from eotile.tile_management.create_tile_shp_from_AOI import *
import geopandas as gp

from shapely import wkt

class TestEOTile(unittest.TestCase):

    def test_create_tiles_file_from_AOI(self):
        output_path = "data/output"
        create_tiles_file_from_AOI(aoi_filepath="data/test_data/illinois.shp",
                        aux_data_dirpath="data/aux_data",
                        out_dirpath=output_path,
                        s2=True, l8=False)
        l8file = gp.read_file(output_path+"/illinois_tiles_L8.shp")
        self.assertEqual(l8file.count().geometry, 18)
        polygon_test = wkt.loads('POLYGON ((-92.76509068409111 41.16654042276556, -92.7655 41.1666, -92.75222227023833'
                                 ' 41.20908647471725, -92.74229393529802 41.24085545623727, -92.31883652795568'
                                 ' 42.59584706653722, -92.30820221301863 42.6298750638544, -92.29559999999999 42.6702,'
                                 ' -92.29516926900379 42.67013726441029, -90.0903 42.349, -90.10354172180196'
                                 ' 42.31079408343177, -90.59568479060121 40.89082942117895, -90.60890000000001 '
                                 '40.8527, -92.76509068409111 41.16654042276556))')
        self.assertTrue(polygon_test in l8file["geometry"])

        s2file = gp.read_file(output_path+"/illinois_tiles_S2.shp")
        self.assertEqual(s2file.count().geometry, 33)
        polygon_test = wkt.loads('POLYGON ((-91.766187862 43.346200009, -90.533217951 43.326246335,'
                                  ' -90.56881764800001 42.426541772, -91.784009944 42.445880705, '
                                  '-91.766187862 43.346200009))')
        self.assertTrue(polygon_test in s2file["geometry"])

    def test_tile_list_utils(self):
        ls2 = create_tiles_list_S2(
            "data/aux_data/S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml",
            "data/test_data/illinois.shp")
        self.assertEqual(['43.346200009',
                         '-91.766187862',
                         '43.326246335',
                         '-90.533217951',
                         '42.426541772',
                         '-90.568817648',
                         '42.445880705',
                         '-91.784009944'], ls2[0].BB)
        self.assertEqual(len(ls2), 33)
        for i in range(len(ls2)):
            self.assertEqual(get_tile(ls2, ls2[i].ID).poly.ExportToWkt(), ls2[i].poly.ExportToWkt())





if __name__ == '__main__':
    unittest.main()
