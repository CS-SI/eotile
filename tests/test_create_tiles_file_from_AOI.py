# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from eotile.utils.tile_list_utils import *
from eotile.tile_management.create_tile_shp_from_AOI import *
import geopandas as gp

class TestEOTile(unittest.TestCase):

    def test_create_tiles_file_from_AOI(self):
        output_path = "data/output"
        create_tiles_file_from_AOI(aoi_filepath="data/test_data/illinois.shp",
                        aux_data_dirpath="data/aux_data",
                        out_dirpath=output_path,
                        s2=True, l8=False)
        l8file = gp.read_file(output_path+"/illinois_tiles_L8.shp")
        self.assertEqual(l8file.count().geometry, 18)
        s2file = gp.read_file(output_path+"/illinois_tiles_S2.shp")
        self.assertEqual(s2file.count().geometry, 33)






if __name__ == '__main__':
    unittest.main()
