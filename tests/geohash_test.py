import math
import random
import unittest

import geohash
from geohash import Coordinates, CellIndices


def print_point(lat: float, lon: float):
    print(f'{lat},{lon},#f00,circle')

def print_boundary(boundary: geohash.CellBoundary):
    print(f'{boundary.start_lat},{boundary.start_lon},#333,circle')
    print(f'{boundary.start_lat},{boundary.end_lon},#333,circle')
    print(f'{boundary.end_lat},{boundary.start_lon},#333,circle')
    print(f'{boundary.end_lat},{boundary.end_lon},#333,circle')

class GeoHashTest(unittest.TestCase):
    def test_calc_geohash(self):
        # Odd precision
        result = geohash.calc_geohash(Coordinates(41.881832, -87.623177), 25)
        self.assertEqual(13275030, result)

        # Even precision
        result = geohash.calc_geohash(Coordinates(41.881832, -87.623177), 20)
        self.assertEqual(414844, result)

    def test_calc_cell_boundary(self):
        # Odd precision
        result: geohash.CellBoundary = geohash.calc_cell_boundary(6300988, 25)
        print_boundary(result)
        self.assertEqual(-41.923828125, result.start_lat)
        self.assertEqual(-41.8798828125, result.end_lat)
        self.assertEqual(-87.626953125, result.start_lon)
        self.assertEqual(-87.5830078125, result.end_lon)

        # Even precision
        result: geohash.CellBoundary = geohash.calc_cell_boundary(196905, 20)
        print_boundary(result)
        self.assertEqual(-42.01171875, result.start_lat)
        self.assertEqual(-41.8359375, result.end_lat)
        self.assertEqual(-87.890625, result.start_lon)
        self.assertEqual(-87.5390625, result.end_lon)

    def test_calc_cell_boundary_adjacent(self):
        result: geohash.CellBoundary = geohash.calc_cell_boundary( 0b00110, 5)
        self.assertEqual(-45, result.start_lat)
        self.assertEqual(0, result.end_lat)
        self.assertEqual(-90, result.start_lon)
        self.assertEqual(-45, result.end_lon)

        result: geohash.CellBoundary = geohash.calc_cell_boundary(0b01100, 5)
        self.assertEqual(-0, result.start_lat)
        self.assertEqual(45, result.end_lat)
        self.assertEqual(-90, result.start_lon)
        self.assertEqual(-45, result.end_lon)

    def test_random_point_to_geohash_to_boundary_even(self):
        self.t_random_point_to_geohash_to_boundary(20)

    def test_random_point_to_geohash_to_boundary_odd(self):
        self.t_random_point_to_geohash_to_boundary(25)

    def t_random_point_to_geohash_to_boundary(self, precision: int):
        random_lat = random.uniform(-90, 90)
        random_lon = random.uniform(-180, 180)

        ghash = geohash.calc_geohash(Coordinates(lat=random_lat, lon=random_lon), precision)
        boundary: geohash.CellBoundary = geohash.calc_cell_boundary(ghash, precision)

        self.assertGreaterEqual(random_lat, boundary.start_lat)
        self.assertLessEqual(random_lat, boundary.end_lat)
        self.assertGreaterEqual(random_lon, boundary.start_lon)
        self.assertLessEqual(random_lon, boundary.end_lon)

        print_point(random_lat, random_lon)
        print_boundary(boundary)

    def test_displace_point_north(self):
        start_coords = Coordinates(lat=41.881832, lon=-87.623177)
        end_coords: Coordinates = geohash.displace_point(start_coords, 1.0, 0)

        self.assertAlmostEqual(41.890825216059184, end_coords.lat, 5)
        self.assertEqual(-87.623177 , end_coords.lon)

        actual_distance = geohash.calc_distance_km(start_coords, end_coords)
        self.assertAlmostEqual(1.0, actual_distance, 5)

    def test_displace_point_south(self):
        start_coords = Coordinates(lat=41.881832, lon=-87.623177)
        end_coords: Coordinates = geohash.displace_point(start_coords, 1.0, math.pi)

        self.assertAlmostEqual(41.87283878394081, end_coords.lat, 5)
        self.assertEqual(-87.623177 , end_coords.lon)

        actual_distance = geohash.calc_distance_km(start_coords, end_coords)
        self.assertAlmostEqual(1.0, actual_distance, 5)

    def test_displace_point_east(self):
        start_coords = Coordinates(lat=41.881832, lon=-87.623177)
        end_coords: Coordinates = geohash.displace_point(start_coords, 1.0, math.pi / 2)

        self.assertAlmostEqual(41.881832, end_coords.lat, 5)
        self.assertAlmostEqual(-87.6110978396452, end_coords.lon, 5)

        actual_distance = geohash.calc_distance_km(start_coords, end_coords)
        self.assertAlmostEqual(1.0, actual_distance, 5)

    def test_displace_point_west(self):
        start_coords = Coordinates(lat=41.881832, lon=-87.623177)
        end_coords: Coordinates = geohash.displace_point(start_coords, 1.0, 3 * math.pi / 2)

        self.assertAlmostEqual(41.881832, end_coords.lat, 5)
        self.assertAlmostEqual(-87.6352561603548, end_coords.lon, 5)

        actual_distance = geohash.calc_distance_km(start_coords, end_coords)
        self.assertAlmostEqual(1.0, actual_distance, 5)

    def test_is_west_of(self):
        self.assertTrue(geohash.is_west_of(origin_point_lon=104, boundary_point_lon=100, test_point_lon=90))

    def test_is_west_of_negative(self):
        self.assertTrue(geohash.is_west_of(origin_point_lon=-104, boundary_point_lon=-110, test_point_lon=-113))

    def test_is_west_of_test_point_crosses_180(self):
        self.assertTrue(geohash.is_west_of(origin_point_lon=-168, boundary_point_lon=-170, test_point_lon=178))

    def test_is_west_of_test_point_crosses_0(self):
        self.assertTrue(geohash.is_west_of(origin_point_lon=12, boundary_point_lon=10, test_point_lon=-3))

    def test_is_west_of_boundary_point_crosses_180(self):
        self.assertFalse(geohash.is_west_of(origin_point_lon=-173, boundary_point_lon=178, test_point_lon=-179))

    def test_is_west_of_boundary_point_crosses_0(self):
        self.assertFalse(geohash.is_west_of(origin_point_lon=7, boundary_point_lon=-2, test_point_lon=1))

    def test_is_east_of(self):
        self.assertTrue(geohash.is_east_of(origin_point_lon=104, boundary_point_lon=110, test_point_lon=114))

    def test_is_east_of_negative(self):
        self.assertTrue(geohash.is_east_of(origin_point_lon=-104, boundary_point_lon=-100, test_point_lon=-95))

    def test_is_east_of_test_point_crosses_180(self):
        self.assertTrue(geohash.is_east_of(origin_point_lon=168, boundary_point_lon=170, test_point_lon=-178))

    def test_is_east_of_test_point_crosses_0(self):
        self.assertTrue(geohash.is_east_of(origin_point_lon=-12, boundary_point_lon=-10, test_point_lon=3))

    def test_is_east_of_boundary_point_crosses_180(self):
        self.assertFalse(geohash.is_east_of(origin_point_lon=173, boundary_point_lon=-178, test_point_lon=179))

    def test_is_east_of_boundary_point_crosses_0(self):
        self.assertFalse(geohash.is_east_of(origin_point_lon=-7, boundary_point_lon=2, test_point_lon=-1))

    def test_geohash_to_cell_indices(self):
        # TODO: Add an example using 5 precision
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0101, 4)
        self.assertEqual(CellIndices(row_index=3, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0100, 4)
        self.assertEqual(CellIndices(row_index=2, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0001, 4)
        self.assertEqual(CellIndices(row_index=1, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0000, 4)
        self.assertEqual(CellIndices(row_index=0, col_index=0), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b0111, 4)
        self.assertEqual(CellIndices(row_index=3, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0110, 4)
        self.assertEqual(CellIndices(row_index=2, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0011, 4)
        self.assertEqual(CellIndices(row_index=1, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b0010, 4)
        self.assertEqual(CellIndices(row_index=0, col_index=1), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b1101, 4)
        self.assertEqual(CellIndices(row_index=3, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1100, 4)
        self.assertEqual(CellIndices(row_index=2, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1001, 4)
        self.assertEqual(CellIndices(row_index=1, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1000, 4)
        self.assertEqual(CellIndices(row_index=0, col_index=2), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b1111, 4)
        self.assertEqual(CellIndices(row_index=3, col_index=3), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1110, 4)
        self.assertEqual(CellIndices(row_index=2, col_index=3), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1011, 4)
        self.assertEqual(CellIndices(row_index=1, col_index=3), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b1010, 4)
        self.assertEqual(CellIndices(row_index=0, col_index=3), indices)

    def test_geohash_to_cell_indices_odd(self):
        indices: CellIndices = geohash.geohash_to_cell_indices(0b01010, 5)
        self.assertEqual(CellIndices(row_index=3, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b01000, 5)
        self.assertEqual(CellIndices(row_index=2, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00010, 5)
        self.assertEqual(CellIndices(row_index=1, col_index=0), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00000, 5)
        self.assertEqual(CellIndices(row_index=0, col_index=0), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b01011, 5)
        self.assertEqual(CellIndices(row_index=3, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b01001, 5)
        self.assertEqual(CellIndices(row_index=2, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00011, 5)
        self.assertEqual(CellIndices(row_index=1, col_index=1), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00001, 5)
        self.assertEqual(CellIndices(row_index=0, col_index=1), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b01110, 5)
        self.assertEqual(CellIndices(row_index=3, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b01100, 5)
        self.assertEqual(CellIndices(row_index=2, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00110, 5)
        self.assertEqual(CellIndices(row_index=1, col_index=2), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b00100, 5)
        self.assertEqual(CellIndices(row_index=0, col_index=2), indices)

        indices: CellIndices = geohash.geohash_to_cell_indices(0b11111, 5)
        self.assertEqual(CellIndices(row_index=3, col_index=7), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b11101, 5)
        self.assertEqual(CellIndices(row_index=2, col_index=7), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b10111, 5)
        self.assertEqual(CellIndices(row_index=1, col_index=7), indices)
        indices: CellIndices = geohash.geohash_to_cell_indices(0b10101, 5)
        self.assertEqual(CellIndices(row_index=0, col_index=7), indices)

    def test_cell_indices_to_geohash(self):
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=0), 4)
        self.assertEqual(0b0101, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=0), 4)
        self.assertEqual(0b0100, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=0), 4)
        self.assertEqual(0b0001, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=0), 4)
        self.assertEqual(0b0000, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=1), 4)
        self.assertEqual(0b0111, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=1), 4)
        self.assertEqual(0b0110, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=1), 4)
        self.assertEqual(0b0011, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=1), 4)
        self.assertEqual(0b0010, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=2), 4)
        self.assertEqual(0b1101, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=2), 4)
        self.assertEqual(0b1100, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=2), 4)
        self.assertEqual(0b1001, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=2), 4)
        self.assertEqual(0b1000, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=3), 4)
        self.assertEqual(0b1111, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=3), 4)
        self.assertEqual(0b1110, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=3), 4)
        self.assertEqual(0b1011, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=3), 4)
        self.assertEqual(0b1010, ghash)

    def test_cell_indices_to_geohash_odd(self):
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=0), 5)
        self.assertEqual(0b01010, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=0), 5)
        self.assertEqual(0b01000, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=0), 5)
        self.assertEqual(0b00010, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=0), 5)
        self.assertEqual(0b00000, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=1), 5)
        self.assertEqual(0b01011, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=1), 5)
        self.assertEqual(0b01001, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=1), 5)
        self.assertEqual(0b00011, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=1), 5)
        self.assertEqual(0b00001, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=2), 5)
        self.assertEqual(0b01110, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=2), 5)
        self.assertEqual(0b01100, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=2), 5)
        self.assertEqual(0b00110, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=2), 5)
        self.assertEqual(0b00100, ghash)

        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=3, col_index=7), 5)
        self.assertEqual(0b11111, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=2, col_index=7), 5)
        self.assertEqual(0b11101, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=1, col_index=7), 5)
        self.assertEqual(0b10111, ghash)
        ghash = geohash.cell_indices_to_geohash(CellIndices(row_index=0, col_index=7), 5)
        self.assertEqual(0b10101, ghash)

    def test_calc_cells_within_radius(self):
        point = Coordinates(41.881832, -87.623177)
        results = geohash.calc_cells_within_radius(point, precision=25, radius=5)

        self.assertEqual({13275030, 13275027, 13275026, 13275031, 13275036, 13275033, 13275032, 13275037, 13275028, 13275025, 13275024, 13275029}, set(results))
