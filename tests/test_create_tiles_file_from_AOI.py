# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from eotile.utils.tile_list_utils import *


class TestSimple(unittest.TestCase):

    def test_create_tiles_file_from_AOI(self):



if __name__ == '__main__':
    unittest.main()
