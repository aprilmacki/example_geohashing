from dataclasses import dataclass

def to_geohash(lat: float, lon: float, precision: int):
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180

    geohash = 0
    for i in range(precision):
        new_bit = 0
        is_lon_bit = i % 2 == 0
        if is_lon_bit:
            # Divide left-right
            lon_mid = (lon_min + lon_max) / 2
            if lon >= lon_mid:
                new_bit = 1
                lon_min = lon_mid
            else:
                new_bit = 0
                lon_max = lon_mid
        else:
            # Divide up-down
            lat_mid = (lat_min + lat_max) / 2
            if lat >= lat_mid:
                new_bit = 0
                lat_min = lat_mid
            else:
                new_bit = 1
                lat_max = lat_mid
        geohash = (geohash << 1) | new_bit
    return geohash

@dataclass
class GeoBoundary:
    start_lat: float
    end_lat: float
    start_lon: float
    end_lon: float

def to_lat_lon_boundary(geohash: int, precision: int) -> GeoBoundary:
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180

    is_lon_bit = True
    for i in range(precision-1, 0, -1):
        bit = geohash & (1 << i)
        if is_lon_bit:
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
                lat_max = lat_mid
            else:
                # Bottom side
                lat_min = lat_mid
        is_lon_bit = not is_lon_bit

    return GeoBoundary(
        start_lat=lat_min,
        end_lat=lat_max,
        start_lon=lon_min,
        end_lon=lon_max,
    )

def calc_neighbors(lat: float, lon: float, radius: float):
    # TODO: Compute north point, west point, south point, and east point.

    # TODO: If west point not included in boundary, add west geohashes until it is included
    # TODO: If east point not included in boundary, add east geohashes until it is included
    # TODO: If north point not included in boundary, add geohashes north of current geohash set until it's included
    # TODO: If south point not included in boundary, add geohashes south of current geohash set until it's included

    pass



