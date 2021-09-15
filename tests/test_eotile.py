# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CS GROUP - France.
#
# This file is part of EOTile.
# See https://github.com/CS-SI/eotile for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
:author: mgerma
:organization: CS GROUP - France
:copyright: 2021 CS GROUP - France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import unittest
from pathlib import Path

from eotile.eotile_module import main as eomain
from eotile.eotiles.eotiles import create_tiles_list_eo, get_tile, write_tiles_bb
from eotile.eotiles.get_bb_from_tile_id import get_tiles_from_tile_id, tile_id_matcher
from eotile.eotiles.utils import build_nominatim_request, input_matcher


class TestEOTile(unittest.TestCase):
    def test_tile_list_utils_s2(self):
        aux_data_dirpath = Path("eotile/data/aux_data")
        filename_tiles_s2 = aux_data_dirpath / "s2_no_overlap.gpkg"
        ls2 = create_tiles_list_eo(
            filename_tiles_s2,
            Path("tests/test_data/illinois.shp"),
        )
        self.assertEqual(len(ls2), 33)

        self.assertTrue(get_tile(ls2, "15TXH") is not None)

        self.assertTrue(get_tile(ls2, "15TXF") is not None)

    def test_tile_list_utils_l8(self):
        aux_data_dirpath = Path("eotile/data/aux_data")
        filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
        l8 = create_tiles_list_eo(
            filename_tiles_l8,
            Path("tests/test_data/illinois.shp"),
        )
        self.assertEqual(len(l8), 18)
        self.assertTrue(get_tile(l8, "25030") is not None)

    def test_read_write_tiles_bb(self):
        aux_data_dirpath = Path("eotile/data/aux_data")
        filename_tiles_l8 = aux_data_dirpath / "l8_tiles.gpkg"
        ll8 = create_tiles_list_eo(
            filename_tiles_l8,
            Path("tests/test_data/illinois.shp"),
        )
        write_tiles_bb(ll8, Path("/tmp/test_read_write.shp"))

        self.assertTrue(get_tile(ll8, "25030") is not None)

    def test_input_matcher(self):
        polygon = "POLYGON((1 1,5 1,5 5,1 5,1 1))"
        mpoly = "MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),(2 2,2 3,3 3,3 2,2 2)),((6 3,9 2,9 4,6 3)))"

        bbox1 = "['36.9701313', '42.5082935', '-91.5130518', '-87.0199244']"
        bbox2 = "'36.9701313', '42.5082935', '-91.5130518', '-87.0199244'"
        bbox3 = "'36.9701313','42.5082935','-91.5130518','-87.0199244'"

        location1 = "Toulouse"
        location2 = "Nowhere"
        location3 = "France"

        tile_id1 = "31TCJ"
        tile_id2 = "199030"

        file1 = "/tmp"
        file2 = "/dev/null"

        test_list = [
            polygon,
            mpoly,
            bbox1,
            bbox2,
            bbox3,
            location1,
            location3,
            tile_id1,
            tile_id2,
            file1,
            file2,
        ]

        with self.assertRaises(ValueError):
            input_matcher(location2)

        out_list = []
        for elt in test_list:
            out_list.append(input_matcher(elt))

        self.assertListEqual(
            out_list,
            [
                "wkt",
                "wkt",
                "bbox",
                "bbox",
                "bbox",
                "location",
                "location",
                "tile_id",
                "tile_id",
                "file",
                "file",
            ],
        )

    def test_tile_id_list_test(self):
        tile_id_list_2 = "31TCJ, 31TCF"
        tile_id_list_3 = "199030, 199029, 197031"
        out_list = []
        for elt in [tile_id_list_2, tile_id_list_3]:
            out_list.append(input_matcher(elt))
        self.assertListEqual(out_list, ["tile_id", "tile_id"])

    def test_id_matcher(self):
        test_id_srtm = "N02W102"
        test_id_cop = "S02W102"
        test_id_s2 = "18SWJ"
        test_id_l8 = "12033"
        test_id_srtm5x5 = "srtm_37_04"
        self.assertEqual(tile_id_matcher(test_id_l8), [False, True, False, False])
        self.assertEqual(tile_id_matcher(test_id_s2), [True, False, False, False])
        self.assertEqual(tile_id_matcher(test_id_cop), [False, False, True, False])
        self.assertEqual(tile_id_matcher(test_id_srtm), [False, False, True, False])
        self.assertEqual(tile_id_matcher(test_id_srtm5x5), [False, False, False, True])

    def test_get_tiles_from_tile_id(self):
        aux_data_dirpath = Path("eotile/data/aux_data")
        output_s2, output_l8, output_dem, output_srtm5x5 = get_tiles_from_tile_id(
            ["31TCJ"], aux_data_dirpath, False, False, dem=True, srtm5x5=True
        )
        self.assertEqual(len(output_s2), 1)
        self.assertEqual(len(output_l8), 4)
        self.assertEqual(len(output_dem), 4)
        self.assertEqual(len(output_srtm5x5), 1)

        output_s2, output_l8, output_dem, output_srtm5x5 = get_tiles_from_tile_id(
            ["200035"], aux_data_dirpath, False, False, dem=True, srtm5x5=True
        )
        self.assertEqual(len(output_s2), 8)
        self.assertEqual(len(output_l8), 1)

    def test_main_module(self):
        output_s2, output_l8, output_dem, output_srtm5x5 = eomain(
            "-74.657, 39.4284, -72.0429, 41.2409",
            no_l8=False,
            no_s2=False,
            dem=True,
            srtm5x5=True,
        )
        self.assertEqual(len(output_s2), 12)
        self.assertEqual(len(output_l8), 9)
        self.assertEqual(len(output_dem), 7)
        self.assertEqual(len(output_srtm5x5), 2)

    def test_main_module_2(self):
        output_s2, output_l8, output_dem, output_srtm5x5 = eomain(
            "tests/test_data/illinois.shp",
            no_l8=False,
            no_s2=False,
            dem=True,
            srtm5x5=True,
        )
        self.assertEqual(len(output_s2), 33)
        self.assertEqual(len(output_l8), 18)
        self.assertEqual(len(output_dem), 27)
        self.assertEqual(len(output_srtm5x5), 4)

    def test_main_module_3(self):
        output_s2, output_l8, output_dem, output_srtm5x5 = eomain(
            "Toulouse",
            no_l8=False,
            no_s2=False,
            dem=True,
            srtm5x5=True,
            threshold=0.1,
        )
        self.assertEqual(len(output_s2), 1)
        self.assertEqual(len(output_l8), 2)
        self.assertEqual(len(output_dem), 1)
        self.assertEqual(len(output_srtm5x5), 1)

    def test_main_module_4(self):
        output_s2, output_l8, output_dem, output_srtm5x5 = eomain(
            "31TCJ",
            no_l8=False,
            no_s2=False,
            dem=True,
            srtm5x5=True,
            min_overlap=0.1,
        )
        self.assertEqual(len(output_s2), 1)
        self.assertEqual(len(output_l8), 3)
        self.assertEqual(len(output_dem), 4)
        self.assertEqual(len(output_srtm5x5), 0)

    def test_build_nominatim_request(self):
        self.assertTrue(
            abs(
                build_nominatim_request(None, "Toulouse", "0.1").area
                - 0.013155945340939995
            )
            < 0.005
        )


if __name__ == "__main__":
    logging.basicConfig(filename="test_eotile.log", level=logging.INFO)
    unittest.main()
