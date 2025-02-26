import math
from copy import copy
from dataclasses import dataclass

@dataclass
class CellBoundary:
    start_lat: float    # North side
    end_lat: float      # South side
    start_lon: float    # West side
    end_lon: float      # East side

@dataclass
class CellIndices:
    # Increasing row index is northward. Rows run latitudinal
    row_index: int
    # Increasing col index is eastward. Cols run longitudinal
    col_index: int

@dataclass
class Coordinates:
    lat: float
    lon: float

EARTH_RADIUS_KM = 6371

def calc_geohash(point: Coordinates, precision: int):
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180

    geohash = 0
    for i in range(precision):
        new_bit = 0
        is_col_bit = i % 2 == 0
        if is_col_bit:
            # Divide left-right
            lon_mid = (lon_min + lon_max) / 2
            if point.lon >= lon_mid:
                new_bit = 1
                lon_min = lon_mid
            else:
                new_bit = 0
                lon_max = lon_mid
        else:
            # Divide up-down
            lat_mid = (lat_min + lat_max) / 2
            if point.lat >= lat_mid:
                new_bit = 1
                lat_min = lat_mid
            else:
                new_bit = 0
                lat_max = lat_mid
        geohash = (geohash << 1) | new_bit
    return geohash

def calc_cell_boundary(cell_geohash: int, precision: int) -> CellBoundary:
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180

    is_col_bit = True
    for i in range(precision-1, -1, -1):
        bit = cell_geohash & (1 << i)
        if is_col_bit:
            lon_mid = (lon_min + lon_max) / 2
            if bit:
                # Right side
                lon_min = lon_mid
            else:
                # Left side
                lon_max = lon_mid
        else:
            lat_mid = (lat_min + lat_max) / 2
            if bit:
                # Top side
                lat_min = lat_mid
            else:
                # Bottom side
                lat_max = lat_mid
        is_col_bit = not is_col_bit

    return CellBoundary(
        start_lat=lat_min,
        end_lat=lat_max,
        start_lon=lon_min,
        end_lon=lon_max,
    )


def is_west_of(origin_point_lon: float, boundary_point_lon: float, test_point_lon) -> bool:
    distance_west_of = lambda origin_lon, point_lon : origin_lon - point_lon + 360 if origin_lon < 0 < point_lon else origin_lon - point_lon
    boundary_dist = distance_west_of(origin_point_lon, boundary_point_lon)
    test_point_dist = distance_west_of(origin_point_lon, test_point_lon)
    return test_point_dist > boundary_dist

def is_east_of(origin_point_lon: float, boundary_point_lon: float, test_point_lon: float) -> bool:
    distance_east_of = lambda origin_lon, point_lon : point_lon - origin_lon + 360 if origin_lon > 0 > point_lon else point_lon - origin_lon
    boundary_dist = distance_east_of(origin_point_lon, boundary_point_lon)
    test_point_dist = distance_east_of(origin_point_lon, test_point_lon)
    return test_point_dist > boundary_dist

def calc_cells_within_radius(point: Coordinates, precision: int, radius: float) -> list[int]:
    '''
    Calculate the geohashes of the cells that contain points within radius km of `coords`.

    This calculates a rectangular boundary around `coords` with dimensions 2*radius by 2*radius.
    Any cell that overlaps this rectanglar boundary is returned.
    A rectangular boundary is used for simplicity, rather than a circular one.

    '''
    ghash = calc_geohash(point, precision)
    ghashes = [ghash]
    ew_hashes = [ghash]
    boundary: CellBoundary = calc_cell_boundary(ghash, precision)

    west_point = displace_point(point, radius, 1.5 * math.pi)
    current_cell_hash = ghash
    while is_west_of(point.lon, boundary.start_lon, west_point.lon):
        neighbor_cell_hash = displace_cell(current_cell_hash, precision, 0, -1)
        neighbor_cell_boundary = calc_cell_boundary(neighbor_cell_hash, precision)
        boundary.start_lon = neighbor_cell_boundary.start_lon
        ghashes.append(neighbor_cell_hash)
        ew_hashes.append(neighbor_cell_hash)
        current_cell_hash = neighbor_cell_hash

    east_point = displace_point(point, radius, math.pi / 2)
    current_cell_hash = ghash
    while is_east_of(point.lon, boundary.end_lon, east_point.lon):
        neighbor_cell_hash = displace_cell(current_cell_hash, precision, 0, 1)
        neighbor_cell_boundary = calc_cell_boundary(neighbor_cell_hash, precision)
        boundary.end_lon = neighbor_cell_boundary.end_lon
        ghashes.append(neighbor_cell_hash)
        ew_hashes.append(neighbor_cell_hash)
        current_cell_hash = neighbor_cell_hash

    north_point = displace_point(point, radius, 0)
    current_ew_hashes = copy(ew_hashes)
    while north_point.lat > boundary.end_lat:
        new_ew_hashes = []
        for ew_hash in current_ew_hashes:
            neighbor_cell_hash = displace_cell(ew_hash, precision, 1, 0)
            ghashes.append(neighbor_cell_hash)
            new_ew_hashes.append(neighbor_cell_hash)

        neighbor_cell_boundary = calc_cell_boundary(new_ew_hashes[0], precision)
        boundary.end_lat = neighbor_cell_boundary.end_lat
        current_ew_hashes = new_ew_hashes

    south_point = displace_point(point, radius, math.pi)
    current_ew_hashes = copy(ew_hashes)
    while south_point.lat < boundary.start_lat:
        new_ew_hashes = []
        for ew_hash in current_ew_hashes:
            neighbor_cell_hash = displace_cell(ew_hash, precision, -1, 0)
            ghashes.append(neighbor_cell_hash)
            new_ew_hashes.append(neighbor_cell_hash)

        neighbor_cell_boundary = calc_cell_boundary(new_ew_hashes[0], precision)
        boundary.start_lat = neighbor_cell_boundary.start_lat
        current_ew_hashes = new_ew_hashes

    return ghashes

def geohash_to_cell_indices(geohash: int, precision: int) -> CellIndices:
    row_index = 0
    col_index = 0

    is_col_index = True
    for i in range(precision-1, -1, -1):
        bit: bool = (geohash & (1 << i)) != 0
        if bit:
            if is_col_index:
                col_index = col_index | (1 << (i // 2))
            else:
                row_index = row_index | (1 << (i // 2))
        is_col_index = not is_col_index

    return CellIndices(row_index=row_index, col_index=col_index)

def cell_indices_to_geohash(cell_indices: CellIndices, precision: int) -> int:
    geohash = 0

    is_col_index = True
    for i in range(precision-1, -1, -1):
        if is_col_index:
            if cell_indices.col_index & (1 << (i // 2)):
                geohash = geohash | (1 << i)
        else:
            if cell_indices.row_index & (1 << (i // 2)):
                geohash = geohash | (1 << i)
        is_col_index = not is_col_index

    return geohash

def displace_cell(geohash: int, precision: int, row_offset: int, col_offset: int) -> int:
    cell_indices: CellIndices = geohash_to_cell_indices(geohash, precision)

    new_cell_indices = CellIndices(row_index=cell_indices.row_index + row_offset, col_index=cell_indices.col_index + col_offset)

    return cell_indices_to_geohash(new_cell_indices, precision)

def displace_point(start_point: Coordinates, offset_km: float, angle_from_n_rad: float) -> Coordinates:
    # See http://www.movable-type.co.uk/scripts/latlong.html
    angular_distance = offset_km / EARTH_RADIUS_KM
    dest_lat_rad = math.asin(math.sin(math.radians(start_point.lat)) * math.cos(angular_distance) + math.cos(math.radians(start_point.lat)) * math.sin(angular_distance) * math.cos(angle_from_n_rad))

    dest_lon_rad = math.radians(start_point.lon) + math.atan2(
        math.sin(angle_from_n_rad) * math.sin(angular_distance) * math.cos(math.radians(start_point.lat)),
        math.cos(angular_distance) - math.sin(math.radians(start_point.lat)) * math.sin(dest_lat_rad)
    )

    dest_lat = math.degrees(dest_lat_rad)
    dest_lon = math.degrees(dest_lon_rad)

    return Coordinates(lat=dest_lat, lon=dest_lon)

def calc_distance_km(point1: Coordinates, point2: Coordinates) -> float:
    # See http://www.movable-type.co.uk/scripts/latlong.html
    delta_lat = math.radians(point2.lat - point1.lat)
    delta_lon = math.radians(point2.lon - point1.lon)

    a = math.pow(math.sin(delta_lat / 2), 2) + math.cos(math.radians(point1.lat)) * math.cos(math.radians(point2.lat)) * math.pow(math.sin(delta_lon / 2), 2)
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) * EARTH_RADIUS_KM
