# -*- coding: utf-8 -*-
"""
:author: mgerma
:organization: CS-Group
:copyright: 2021 CS-Group France. All rights reserved.
:license: see LICENSE file.
"""

import logging
import unittest
from pathlib import Path

from eotile.eotile_cli import input_matcher
from eotile.eotiles.eotiles import (
    create_tiles_list_eo,
    create_tiles_list_s2,
    get_tile,
    read_tile_list_from_file,
    write_tiles_bb,
)


class TestEOTile(unittest.TestCase):
    def test_tile_list_utils_s2(self):
        ls2 = create_tiles_list_s2(
            Path(
                "eotile/data/aux_data/S2A_OPER_GIP_TILPAR_MPC__20140923T000000_V20000101T000000_20200101T000000_B00.xml"
            ),
            Path("tests/test_data/illinois.shp"),
        )
        self.assertEqual(
            [
                "43.346200009",
                "-91.766187862",
                "43.326246335",
                "-90.533217951",
                "42.426541772",
                "-90.568817648",
                "42.445880705",
                "-91.784009944",
            ],
            ls2[0].BB,
        )
        self.assertEqual(len(ls2), 33)
        self.assertTrue(
            get_tile(ls2, ls2[1].ID).BB
            in [
                [
                    "43.346200009",
                    "-91.766187862",
                    "43.326246335",
                    "-90.533217951",
                    "42.426541772",
                    "-90.568817648",
                    "42.445880705",
                    "-91.784009944",
                ],
                [
                    "43.326246335",
                    "-90.533217951",
                    "43.293031723",
                    "-89.301928866",
                    "42.394349602",
                    "-89.355217574",
                    "42.426541772",
                    "-90.568817648",
                ],
                [
                    "42.426541772",
                    "-90.568817648",
                    "42.394349602",
                    "-89.355217574",
                    "41.495474123",
                    "-89.406124539",
                    "41.526672311",
                    "-90.602824028",
                ],
                [
                    "41.54541366",
                    "-91.801033713",
                    "41.526672311",
                    "-90.602824028",
                    "40.626639727",
                    "-90.635319213",
                    "40.64479965",
                    "-91.817300377",
                ],
                [
                    "41.526672311",
                    "-90.602824028",
                    "41.495474123",
                    "-89.406124539",
                    "40.596408719",
                    "-89.454772217",
                    "40.626639727",
                    "-90.635319213",
                ],
                [
                    "40.64479965",
                    "-91.817300377",
                    "40.626639727",
                    "-90.635319213",
                    "39.726445843",
                    "-90.666379316",
                    "39.744039563",
                    "-91.832848125",
                ],
                [
                    "40.626639727",
                    "-90.635319213",
                    "40.596408719",
                    "-89.454772217",
                    "39.697156754",
                    "-89.501274127",
                    "39.726445843",
                    "-90.666379316",
                ],
                [
                    "39.744039563",
                    "-91.832848125",
                    "39.726445843",
                    "-90.666379316",
                    "38.826092537",
                    "-90.696074964",
                    "38.84313441",
                    "-91.847712385",
                ],
                [
                    "39.726445843",
                    "-90.666379316",
                    "39.697156754",
                    "-89.501274127",
                    "38.797721547",
                    "-89.545735626",
                    "38.826092537",
                    "-90.696074964",
                ],
                [
                    "38.826092537",
                    "-90.696074964",
                    "38.797721547",
                    "-89.545735626",
                    "37.898106377",
                    "-89.5882546",
                    "37.92558175",
                    "-90.724471764",
                ],
                [
                    "37.92558175",
                    "-90.724471764",
                    "37.898106377",
                    "-89.5882546",
                    "36.998314508",
                    "-89.628922085",
                    "37.024915488",
                    "-90.75163072",
                ],
                [
                    "43.326246335",
                    "-89.466782049",
                    "43.346200009",
                    "-88.233812138",
                    "42.445880705",
                    "-88.215990056",
                    "42.426541772",
                    "-89.431182352",
                ],
                [
                    "43.346200009",
                    "-88.233812138",
                    "43.352855392",
                    "-87",
                    "42.452330961",
                    "-87",
                    "42.445880705",
                    "-88.215990056",
                ],
                [
                    "42.394349602",
                    "-90.644782426",
                    "42.426541772",
                    "-89.431182352",
                    "41.526672311",
                    "-89.397175972",
                    "41.495474123",
                    "-90.593875461",
                ],
                [
                    "42.426541772",
                    "-89.431182352",
                    "42.445880705",
                    "-88.215990056",
                    "41.54541366",
                    "-88.198966287",
                    "41.526672311",
                    "-89.397175972",
                ],
                [
                    "42.445880705",
                    "-88.215990056",
                    "42.452330961",
                    "-87",
                    "41.551664522",
                    "-87",
                    "41.54541366",
                    "-88.198966287",
                ],
                [
                    "41.495474123",
                    "-90.593875461",
                    "41.526672311",
                    "-89.397175972",
                    "40.626639727",
                    "-89.364680787",
                    "40.596408719",
                    "-90.545227783",
                ],
                [
                    "41.526672311",
                    "-89.397175972",
                    "41.54541366",
                    "-88.198966287",
                    "40.64479965",
                    "-88.182699623",
                    "40.626639727",
                    "-89.364680787",
                ],
                [
                    "41.54541366",
                    "-88.198966287",
                    "41.551664522",
                    "-87",
                    "40.650856516",
                    "-87",
                    "40.64479965",
                    "-88.182699623",
                ],
                [
                    "40.596408719",
                    "-90.545227783",
                    "40.626639727",
                    "-89.364680787",
                    "39.726445843",
                    "-89.333620684",
                    "39.697156754",
                    "-90.498725873",
                ],
                [
                    "40.626639727",
                    "-89.364680787",
                    "40.64479965",
                    "-88.182699623",
                    "39.744039563",
                    "-88.167151875",
                    "39.726445843",
                    "-89.333620684",
                ],
                [
                    "40.64479965",
                    "-88.182699623",
                    "40.650856516",
                    "-87",
                    "39.749907519",
                    "-87",
                    "39.744039563",
                    "-88.167151875",
                ],
                [
                    "39.697156754",
                    "-90.498725873",
                    "39.726445843",
                    "-89.333620684",
                    "38.826092537",
                    "-89.303925036",
                    "38.797721547",
                    "-90.454264374",
                ],
                [
                    "39.726445843",
                    "-89.333620684",
                    "39.744039563",
                    "-88.167151875",
                    "38.84313441",
                    "-88.152287615",
                    "38.826092537",
                    "-89.303925036",
                ],
                [
                    "39.744039563",
                    "-88.167151875",
                    "39.749907519",
                    "-87",
                    "38.848818252",
                    "-87",
                    "38.84313441",
                    "-88.152287615",
                ],
                [
                    "38.797721547",
                    "-90.454264374",
                    "38.826092537",
                    "-89.303925036",
                    "37.92558175",
                    "-89.275528236",
                    "37.898106377",
                    "-90.4117454",
                ],
                [
                    "38.826092537",
                    "-89.303925036",
                    "38.84313441",
                    "-88.152287615",
                    "37.94208532",
                    "-88.138073932",
                    "37.92558175",
                    "-89.275528236",
                ],
                [
                    "38.84313441",
                    "-88.152287615",
                    "38.848818252",
                    "-87",
                    "37.947589572",
                    "-87",
                    "37.94208532",
                    "-88.138073932",
                ],
                [
                    "37.898106377",
                    "-90.4117454",
                    "37.92558175",
                    "-89.275528236",
                    "37.024915488",
                    "-89.24836928",
                    "36.998314508",
                    "-90.371077915",
                ],
                [
                    "37.92558175",
                    "-89.275528236",
                    "37.94208532",
                    "-88.138073932",
                    "37.040893543",
                    "-88.12448023",
                    "37.024915488",
                    "-89.24836928",
                ],
                [
                    "37.94208532",
                    "-88.138073932",
                    "37.947589572",
                    "-87",
                    "37.046222476",
                    "-87",
                    "37.040893543",
                    "-88.12448023",
                ],
                [
                    "36.998314508",
                    "-90.371077915",
                    "37.024915488",
                    "-89.24836928",
                    "36.124095832",
                    "-89.222391385",
                    "36.098349195",
                    "-90.332177171",
                ],
                [
                    "37.024915488",
                    "-89.24836928",
                    "37.040893543",
                    "-88.12448023",
                    "36.13956045",
                    "-88.111478032",
                    "36.124095832",
                    "-89.222391385",
                ],
            ]
        )

        self.assertTrue(
            ls2[1].ID
            in [
                "15TXH",
                "15TYH",
                "15TYG",
                "15TXF",
                "15TYF",
                "15TXE",
                "15TYE",
                "15SXD",
                "15SYD",
                "15SYC",
                "15SYB",
                "16TCN",
                "16TDN",
                "16TBM",
                "16TCM",
                "16TDM",
                "16TBL",
                "16TCL",
                "16TDL",
                "16TBK",
                "16TCK",
                "16TDK",
                "16SBJ",
                "16SCJ",
                "16SDJ",
                "16SBH",
                "16SCH",
                "16SDH",
                "16SBG",
                "16SCG",
                "16SDG",
                "16SBF",
                "16SCF",
            ]
        )

    def test_tile_list_utils_l8(self):
        l8 = create_tiles_list_eo(
            Path("eotile/data/aux_data/wrs2_descending/"),
            Path("tests/test_data/illinois.shp"),
            "L8",
        )
        self.assertEqual(len(l8), 18)
        self.assertTrue(
            l8[1].ID
            in [
                "25030",
                "25031",
                "25032",
                "25033",
                "23030",
                "23031",
                "23032",
                "23033",
                "23034",
                "24030",
                "24031",
                "24032",
                "24033",
                "24034",
                "22031",
                "22032",
                "22033",
                "22034",
            ]
        )

    def test_read_write_tiles_bb(self):
        ll8 = create_tiles_list_eo(
            Path("eotile/data/aux_data/wrs2_descending/"),
            Path("tests/test_data/illinois.shp"),
            "L8",
        )
        write_tiles_bb(ll8, Path("/tmp/test_read_write.shp"))

        read_file = read_tile_list_from_file(Path("tests/test_data2/illinois2.shp"))
        id_list = []
        for elt in read_file:
            id_list.append(elt.ID)
        self.assertTrue("25030" in id_list)

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


if __name__ == "__main__":
    logging.basicConfig(filename="test_eotile.log", level=logging.INFO)
    unittest.main()
