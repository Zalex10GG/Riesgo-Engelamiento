import pytest
import numpy as np
import xarray as xr
import sys
from pathlib import Path

# Añadir src al path para los tests
sys.path.append(str(Path(__file__).parent.parent / "src"))

from engelamiento.detection.trajectory import (
    calculate_orthodromic_points, 
    haversine_distance, 
    pressure_to_altitude_ft,
    get_flight_profile
)

def test_haversine():
    # Madrid to Barcelona approx
    d = haversine_distance(40.41, -3.70, 41.38, 2.17)
    assert 500 < d < 510

def test_orthodromic_points():
    points = calculate_orthodromic_points(40, -3, 40, 2, num_points=10)
    assert len(points) == 10
    assert np.isclose(points[0][0], 40.0)
    assert np.isclose(points[0][1], -3.0)
    assert np.isclose(points[-1][0], 40.0)
    assert np.isclose(points[-1][1], 2.0)

def test_pressure_conversion():
    # 1013.25 hPa -> 0 ft
    alt = pressure_to_altitude_ft(101325.0)
    assert abs(alt) < 1.0
    
    # Approx 300 hPa -> 30000 ft
    alt2 = pressure_to_altitude_ft(30000.0)
    assert 29000 < alt2 < 31000

def test_flight_profile():
    profile = get_flight_profile(1000, target_fl=290)
    # 20% of 1000 is 200km. At 200km should be target alt.
    # We sample 101 points, so index 20 is exactly 20%
    assert profile[0][1] == 0
    assert profile[20][1] == 29000
    assert profile[50][1] == 29000
    assert profile[80][1] == 29000
    assert profile[100][1] == 0
