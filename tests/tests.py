import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aeroplane import Aeroplane
from file_manager import JSONFileManager, CSVFileManager


class TestAeroplaneCreation(unittest.TestCase):
    """Тесты создания и валидации объектов Aeroplane."""

    def test_valid_creation(self):
        p = Aeroplane("abc123", "UAL123", "United States", 10.5, 50.2, 10000, 250)
        self.assertEqual(p.icao24, "abc123")
        self.assertEqual(p.callsign, "UAL123")
        self.assertEqual(p.origin_country, "United States")
        self.assertEqual(p.longitude, 10.5)
        self.assertEqual(p.latitude, 50.2)
        self.assertEqual(p.altitude, 10000)
        self.assertEqual(p.velocity, 250)
        self.assertFalse(p.on_ground)

    def test_callsign_none(self):
        p = Aeroplane("abc123", None, "Germany", None, None, None, None)
        self.assertEqual(p.callsign, "N/A")

    def test_invalid_icao24(self):
        with self.assertRaises(ValueError):
            Aeroplane("", "CS", "Germany", 1, 2, 100, 50)

    def test_invalid_icao24_not_string(self):
        with self.assertRaises(ValueError):
            Aeroplane(123, "CS", "Germany", 1, 2, 100, 50)

    def test_negative_altitude(self):
        with self.assertRaises(ValueError):
            Aeroplane("abc", "CS", "Germany", 1, 2, -100, 50)

    def test_negative_velocity(self):
        with self.assertRaises(ValueError):
            Aeroplane("abc", "CS", "Germany", 1, 2, 100, -50)

    def test_invalid_coord_type(self):
        with self.assertRaises(ValueError):
            Aeroplane("abc", "CS", "Germany", "not_a_number", 2, 100, 50)

    def test_none_coords_allowed(self):
        p = Aeroplane("abc", "CS", "Germany", None, None, None, None)
        self.assertIsNone(p.longitude)
        self.assertIsNone(p.latitude)
        self.assertIsNone(p.altitude)
        self.assertIsNone(p.velocity)


class TestAeroplaneComparison(unittest.TestCase):
    """Тесты методов сравнения по скорости и высоте."""

    def setUp(self):
        self.fast_high = Aeroplane("a1", "F1", "USA", 10, 20, 11000, 300)
        self.slow_low = Aeroplane("a2", "F2", "USA", 10, 20, 5000, 150)
        self.same = Aeroplane("a3", "F3", "USA", 10, 20, 11000, 300)

    def test_less_than_by_velocity(self):
        self.assertTrue(self.slow_low < self.fast_high)
        self.assertFalse(self.fast_high < self.slow_low)

    def test_greater_than_by_velocity(self):
        self.assertTrue(self.fast_high > self.slow_low)
        self.assertFalse(self.slow_low > self.fast_high)

    def test_le_by_velocity(self):
        self.assertTrue(self.slow_low <= self.fast_high)
        self.assertTrue(self.same <= self.fast_high)

    def test_ge_by_velocity(self):
        self.assertTrue(self.fast_high >= self.slow_low)
        self.assertTrue(self.same >= self.fast_high)

    def test_eq_by_velocity(self):
        self.assertTrue(self.fast_high == self.same)
        self.assertFalse(self.fast_high == self.slow_low)

    def test_is_higher_than(self):
        self.assertTrue(self.fast_high.is_higher_than(self.slow_low))
        self.assertFalse(self.slow_low.is_higher_than(self.fast_high))

    def test_is_lower_than(self):
        self.assertTrue(self.slow_low.is_lower_than(self.fast_high))
        self.assertFalse(self.fast_high.is_lower_than(self.slow_low))

    def test_compare_different_type(self):
        with self.assertRaises(TypeError):
            self.fast_high < "not_a_plane"

    def test_eq_with_non_aeroplane(self):
        self.assertFalse(self.fast_high == 42)


class TestAeroplaneSerialization(unittest.TestCase):
    """Тесты сериализации и десериализации."""

    def test_to_dict_and_back(self):
        p = Aeroplane("abc123", "UAL", "USA", 10.5, 50.2, 10000, 250, True)
        d = p.to_dict()
        self.assertEqual(d["icao24"], "abc123")
        self.assertEqual(d["callsign"], "UAL")
        self.assertTrue(d["on_ground"])
        p2 = Aeroplane.from_dict(d)
        self.assertEqual(p2.icao24, p.icao24)
        self.assertEqual(p2.callsign, p.callsign)
        self.assertEqual(p2.altitude, p.altitude)
        self.assertEqual(p2.velocity, p.velocity)
        self.assertEqual(p2.on_ground, p.on_ground)


class TestJSONFileManager(unittest.TestCase):
    """Тесты JSONFileManager."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            json.dump([], f)
        self.manager = JSONFileManager(self.tmp.name)
        self.plane1 = Aeroplane("id1", "CS1", "USA", 10, 20, 11000, 300)
        self.plane2 = Aeroplane("id2", "CS2", "Germany", 15, 25, 5000, 150)
        self.plane3 = Aeroplane("id3", "CS3", "USA", 30, 40, 8000, 220)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_add_and_get_all(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        result = self.manager.get_all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].icao24, "id1")
        self.assertEqual(result[1].origin_country, "Germany")

    def test_get_by_criteria(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        self.manager.add(self.plane3)
        usa = self.manager.get_by_criteria({"origin_country": "USA"})
        self.assertEqual(len(usa), 2)
        self.assertTrue(all(p.origin_country == "USA" for p in usa))

    def test_delete(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        self.manager.add(self.plane3)
        removed = self.manager.delete({"origin_country": "USA"})
        self.assertEqual(removed, 2)
        remaining = self.manager.get_all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].origin_country, "Germany")

    def test_delete_nonexistent(self):
        self.manager.add(self.plane1)
        removed = self.manager.delete({"origin_country": "Japan"})
        self.assertEqual(removed, 0)

    def test_db_stub_methods(self):
        with self.assertRaises(NotImplementedError):
            self.manager.connect()
        with self.assertRaises(NotImplementedError):
            self.manager.disconnect()


class TestCSVFileManager(unittest.TestCase):
    """Тесты CSVFileManager."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        import csv
        with open(self.tmp.name, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSVFileManager.FIELDS)
            writer.writeheader()
        self.manager = CSVFileManager(self.tmp.name)
        self.plane1 = Aeroplane("id1", "CS1", "USA", 10.0, 20.0, 11000.0, 300.0)
        self.plane2 = Aeroplane("id2", "CS2", "Germany", 15.0, 25.0, 5000.0, 150.0)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_add_and_get_all(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        result = self.manager.get_all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].icao24, "id1")
        self.assertEqual(result[1].origin_country, "Germany")
        self.assertAlmostEqual(result[0].altitude, 11000.0)
        self.assertAlmostEqual(result[0].velocity, 300.0)

    def test_get_by_criteria(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        usa = self.manager.get_by_criteria({"origin_country": "USA"})
        self.assertEqual(len(usa), 1)
        self.assertEqual(usa[0].icao24, "id1")

    def test_delete(self):
        self.manager.add(self.plane1)
        self.manager.add(self.plane2)
        removed = self.manager.delete({"origin_country": "USA"})
        self.assertEqual(removed, 1)
        remaining = self.manager.get_all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].origin_country, "Germany")


class TestParseAeroplanes(unittest.TestCase):
    """Тесты parse_aeroplanes из main.py."""

    def test_parse_valid(self):
        raw = [
            ["abc123", "UAL123", "United States", "US", 1600, 10.5, 50.2, 10000, False, 250, 0, False],
            ["def456", None, "Germany", "DE", 1600, 15.0, 25.0, 5000, True, 0, 0, False],
            ["bad", "CS", "France", "FR", 1600, "not_float", 0, 100, False, 50, 0, False],
        ]
        from main import parse_aeroplanes
        planes = parse_aeroplanes(raw)
        self.assertEqual(len(planes), 2)
        self.assertEqual(planes[0].callsign, "UAL123")
        self.assertEqual(planes[1].callsign, "N/A")

    def test_parse_empty(self):
        from main import parse_aeroplanes
        self.assertEqual(parse_aeroplanes([]), [])


if __name__ == "__main__":
    unittest.main()
