import random
import unittest

import geohash

def print_point(lat: float, lon: float):
    print(f'{lat},{lon},#f00,circle')

def print_boundary(boundary: geohash.GeoBoundary):
    print(f'{boundary.start_lat},{boundary.start_lon},#333,circle')
    print(f'{boundary.start_lat},{boundary.end_lon},#333,circle')
    print(f'{boundary.end_lat},{boundary.start_lon},#333,circle')
    print(f'{boundary.end_lat},{boundary.end_lon},#333,circle')

class GeoHashTest(unittest.TestCase):
    def test_to_geohash_odd(self):
        result = geohash.to_geohash(41.881832, -87.623177, 25)
        self.assertEqual(6300988, result)

    def test_to_geohash_even(self):
        result = geohash.to_geohash(41.881832, -87.623177, 20)
        self.assertEqual(196905, result)

    def test_to_boundary_odd(self):
        result: geohash.GeoBoundary = geohash.to_lat_lon_boundary(6300988, 25)

        print_boundary(result)

        self.assertEqual(41.8798828125, result.start_lat)
        self.assertEqual(41.923828125, result.end_lat)
        self.assertEqual(-87.626953125, result.start_lon)
        self.assertEqual(-87.5390625, result.end_lon)

    def test_to_boundary_even(self):
        result: geohash.GeoBoundary = geohash.to_lat_lon_boundary(196905, 20)

        print_boundary(result)

        self.assertEqual(41.8359375, result.start_lat)
        self.assertEqual(42.1875, result.end_lat)
        self.assertEqual(-87.890625, result.start_lon)
        self.assertEqual(-87.5390625, result.end_lon)

    def test_random_conversion_odd(self):
        random_lat = random.uniform(-90, 90)
        random_lon = random.uniform(-180, 180)

        ghash = geohash.to_geohash(random_lat, random_lon, 25)
        boundary: geohash.GeoBoundary = geohash.to_lat_lon_boundary(ghash, 25)

        self.assertGreaterEqual(random_lat, boundary.start_lat)
        self.assertLessEqual(random_lat, boundary.end_lat)
        self.assertGreaterEqual(random_lon, boundary.start_lon)
        self.assertLessEqual(random_lon, boundary.end_lon)

        print_point(random_lat, random_lon)
        print_boundary(boundary)

    def test_random_conversion_even(self):
        random_lat = random.uniform(-90, 90)
        random_lon = random.uniform(-180, 180)

        ghash = geohash.to_geohash(random_lat, random_lon, 20)
        boundary: geohash.GeoBoundary = geohash.to_lat_lon_boundary(ghash, 20)

        self.assertGreaterEqual(random_lat, boundary.start_lat)
        self.assertLessEqual(random_lat, boundary.end_lat)
        self.assertGreaterEqual(random_lon, boundary.start_lon)
        self.assertLessEqual(random_lon, boundary.end_lon)

        print_point(random_lat, random_lon)
        print_boundary(boundary)


