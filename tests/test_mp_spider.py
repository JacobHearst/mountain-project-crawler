import unittest
from unittest.mock import MagicMock

from mp_scraper.spiders.mp import MpSpider

from tests import compare_item_iter


class TestMpSpider(unittest.TestCase):
    def test_extract_id(self):
        spider = MpSpider()
        cases = [
            (".com/route/105717310/stolen-chimney", 105717310),
            (".com/area/105716859/ancient-art", 105716859),
            (".com", None),
            (".com/directory/105716859/route-or-area", None)
        ]

        for case in cases:
            with self.subTest(case=case):
                result = spider.extract_id(case[0])
                self.assertEqual(result, case[1])

    def test_extract_precip(self):
        spider = MpSpider()
        data = [
            ["January", 1, 2],
            ["February", 3, 4],
            ["March", 5, 6],
            ["April", 7, 8],
            ["May", 9, 10],
            ["June", 11, 12],
            ["July", 13, 14],
            ["August", 15, 16],
            ["September", 17, 18],
            ["October", 19, 20],
            ["November", 21, 22],
            ["December", 23, 24]
        ]

        spider.extract_monthly_data = MagicMock(return_value=data)

        expected = [
            {"month": 1, "avg_low": 1, "avg_high": 2},
            {"month": 2, "avg_low": 3, "avg_high": 4},
            {"month": 3, "avg_low": 5, "avg_high": 6},
            {"month": 4, "avg_low": 7, "avg_high": 8},
            {"month": 5, "avg_low": 9, "avg_high": 10},
            {"month": 6, "avg_low": 11, "avg_high": 12},
            {"month": 7, "avg_low": 13, "avg_high": 14},
            {"month": 8, "avg_low": 15, "avg_high": 16},
            {"month": 9, "avg_low": 17, "avg_high": 18},
            {"month": 10, "avg_low": 19, "avg_high": 20},
            {"month": 11, "avg_low": 21, "avg_high": 22},
            {"month": 12, "avg_low": 23, "avg_high": 24}
        ]

        result = spider.extract_monthly_avg(None, "dataPrecip")
        compare_item_iter(self, expected, result)

    def test_extract_temps(self):
        spider = MpSpider()
        data = [
            ["January", 2, 1],
            ["February", 4, 3],
            ["March", 6, 5],
            ["April", 8, 7],
            ["May", 10, 9],
            ["June", 12, 11],
            ["July", 14, 13],
            ["August", 16, 15],
            ["September", 18, 17],
            ["October", 20, 19],
            ["November", 22, 21],
            ["December", 24, 23]
        ]

        spider.extract_monthly_data = MagicMock(return_value=data)

        expected = [
            {"month": 1, "avg_low": 1, "avg_high": 2},
            {"month": 2, "avg_low": 3, "avg_high": 4},
            {"month": 3, "avg_low": 5, "avg_high": 6},
            {"month": 4, "avg_low": 7, "avg_high": 8},
            {"month": 5, "avg_low": 9, "avg_high": 10},
            {"month": 6, "avg_low": 11, "avg_high": 12},
            {"month": 7, "avg_low": 13, "avg_high": 14},
            {"month": 8, "avg_low": 15, "avg_high": 16},
            {"month": 9, "avg_low": 17, "avg_high": 18},
            {"month": 10, "avg_low": 19, "avg_high": 20},
            {"month": 11, "avg_low": 21, "avg_high": 22},
            {"month": 12, "avg_low": 23, "avg_high": 24}
        ]

        result = spider.extract_monthly_avg(None, "dataTemps")
        compare_item_iter(self, expected, result)

    def test_extract_climb_season(self):
        spider = MpSpider()
        data = [
            ["October", 19, 20],
            ["March", 5, 6],
            ["April", 7, 8],
            ["July", 13, 14],
            ["January", 1, 2],
            ["June", 11, 12],
            ["February", 3, 4],
            ["December", 23, 24],
            ["May", 9, 10],
            ["August", 15, 16],
            ["November", 21, 22],
            ["September", 17, 18],
        ]

        spider.extract_monthly_data = MagicMock(return_value=data)

        expected = [
            {"month": 10, "popularity": 19},
            {"month": 3, "popularity": 5},
            {"month": 4, "popularity": 7},
            {"month": 7, "popularity": 13},
            {"month": 1, "popularity": 1},
            {"month": 6, "popularity": 11},
            {"month": 2, "popularity": 3},
            {"month": 12, "popularity": 23},
            {"month": 5, "popularity": 9},
            {"month": 8, "popularity": 15},
            {"month": 11, "popularity": 21},
            {"month": 9, "popularity": 17}
        ]

        result = spider.extract_climb_season(None)
        compare_item_iter(self, expected, result)

    def test_empty_monthly_vals(self):
        spider = MpSpider()
        spider.extract_monthly_data = MagicMock(return_value=[[]])

        temps = spider.extract_monthly_avg(None, "dataTemps")
        precip = spider.extract_monthly_avg(None, "dataPrecip")
        climb_season = spider.extract_climb_season(None)

        self.assertEqual([], temps)
        self.assertEqual([], precip)
        self.assertEqual([], climb_season)


if __name__ == "__main__":
    unittest.main()
