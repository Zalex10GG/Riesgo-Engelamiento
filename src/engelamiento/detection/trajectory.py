import numpy as np
import xarray as xr
from typing import List, Tuple, Dict


def calculate_orthodromic_points(
    lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 50
) -> List[Tuple[float, float]]:
    """Calcula puntos intermedios en la ortodrómica entre dos coordenadas."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    d = 2 * np.arcsin(
        np.sqrt(
            np.sin((lat1 - lat2) / 2) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin((lon1 - lon2) / 2) ** 2
        )
    )

    fractions = np.linspace(0, 1, num_points)
    points = []

    for f in fractions:
        if d == 0:
            points.append((np.degrees(lat1), np.degrees(lon1)))
            continue
            
        a = np.sin((1 - f) * d) / np.sin(d)
        b = np.sin(f * d) / np.sin(d)
        x = a * np.cos(lat1) * np.cos(lon1) + b * np.cos(lat2) * np.cos(lon2)
        y = a * np.cos(lat1) * np.sin(lon1) + b * np.cos(lat2) * np.sin(lon2)
        z = a * np.sin(lat1) + b * np.sin(lat2)
        
        lat = np.arctan2(z, np.sqrt(x**2 + y**2))
        lon = np.arctan2(y, x)
        points.append((float(np.degrees(lat)), float(np.degrees(lon))))

    return points


def haversine_distance(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def pressure_to_altitude_ft(p_pa: float) -> float:
    """Convierte presión en Pascales a altitud en pies usando atmósfera estándar."""
    # h = (1 - (P/P0)^0.190284) * 145366.45
    p0 = 101325.0
    if p_pa <= 0:
        return 0.0
    h_ft = (1.0 - (p_pa / p0) ** 0.190284) * 145366.45
    return float(h_ft)


def get_flight_profile(total_dist_km: float, target_fl: int = 290) -> List[Tuple[float, float]]:
    """Genera perfil de vuelo 20%-60%-20% hasta FL target."""
    target_ft = target_fl * 100
    points = []
    
    # Muestrear el perfil de vuelo en 100 puntos
    for f in np.linspace(0, 1, 101):
        dist = f * total_dist_km
        if f <= 0.2:  # Ascenso (de 0 a 0.2)
            alt = (f / 0.2) * target_ft
        elif f <= 0.8:  # Crucero (de 0.2 a 0.8)
            alt = target_ft
        else:  # Descenso (de 0.8 a 1.0)
            # A medida que f va de 0.8 a 1.0, (1-f)/0.2 va de 1.0 a 0.0
            alt = ((1.0 - f) / 0.2) * target_ft
        points.append((float(dist), float(alt)))
    return points


def calculate_vertical_profile(
    ds: xr.Dataset, 
    time_idx: int, 
    lat1: float, lon1: float, lat2: float, lon2: float,
    corridor_width_km: float = 15.0
) -> Dict:
    """Calcula el perfil vertical de engelamiento a lo largo de un corredor de trayectoria."""
    # 1. Calcular distancia total para definir resolución
    total_dist = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Muestrear cada 5km aprox
    num_points = max(20, int(total_dist / 5.0))
    path_points = calculate_orthodromic_points(lat1, lon1, lat2, lon2, num_points=num_points)
    
    # 2. Calcular distancias acumuladas para los puntos de la ortodrómica
    distances = [0.0]
    for i in range(1, len(path_points)):
        prev = path_points[i-1]
        curr = path_points[i]
        d = haversine_distance(prev[0], prev[1], curr[0], curr[1])
        distances.append(distances[-1] + d)
    
    # 3. Preparar datos WRF
    vars_to_load = ["TK", "P", "PB", "QRAIN", "QCLOUD", "XLAT", "XLONG"]
    subset = ds[vars_to_load].isel(Time=time_idx)
    
    # Extraer arrays como copia para evitar problemas de índices de xarray
    lat_vals = np.array(subset["XLAT"].values)
    lon_vals = np.array(subset["XLONG"].values)
    tk_vals = np.array(subset["TK"].values)
    p_vals = np.array((subset["P"] + subset["PB"]).values)
    qr_vals = np.array(subset["QRAIN"].values)
    qc_vals = np.array(subset["QCLOUD"].values)
    
    # 4. Encontrar celdas relevantes (dentro del corredor de 15km)
    lats_path = [float(p[0]) for p in path_points]
    lons_path = [float(p[1]) for p in path_points]
    
    lat_min, lat_max = min(lats_path) - 1.0, max(lats_path) + 1.0
    lon_min, lon_max = min(lons_path) - 1.0, max(lons_path) + 1.0
    
    spatial_mask = (lat_vals >= lat_min) & (lat_vals <= lat_max) & \
                   (lon_vals >= lon_min) & (lon_vals <= lon_max)
    
    # Índices de celdas que caen en el bounding box
    y_idxs, x_idxs = np.where(spatial_mask)
    
    profile_hits = {} # Key: (dist_bin, alt_bin) -> max_lwc_data
    
    # 5. Para cada celda candidata, encontrar su punto más cercano en la ruta
    lats_path_arr = np.array(lats_path)
    lons_path_arr = np.array(lons_path)
    dist_path_arr = np.array(distances)

    path_coords = np.stack([lats_path_arr, lons_path_arr], axis=1)

    print(f"DEBUG: Calculando perfil para {len(y_idxs)} celdas candidatas")
    print(f"DEBUG: Punto A (dist 0): {path_coords[0]} | Solicitado: {lat1}, {lon1}")
    print(f"DEBUG: Punto B (dist max): {path_coords[-1]} | Solicitado: {lat2}, {lon2}")

    for y, x in zip(y_idxs, x_idxs):
        c_lat, c_lon = float(lat_vals[y, x]), float(lon_vals[y, x])
        
        # Distancia euclídea aproximada para encontrar el índice en el array de la ruta
        d_sq = np.sum((path_coords - np.array([c_lat, c_lon]))**2, axis=1)
        nearest_idx = np.argmin(d_sq)
        
        # Calcular distancia real (Haversine) al punto más cercano de la ruta
        dist_to_route = haversine_distance(c_lat, c_lon, lats_path_arr[nearest_idx], lons_path_arr[nearest_idx])
        
        if dist_to_route <= corridor_width_km:
            dist_on_path = dist_path_arr[nearest_idx]
            
            # Recorrer vertical
            for level in range(tk_vals.shape[0]):
                temp = tk_vals[level, y, x]
                qr = qr_vals[level, y, x]
                qc = qc_vals[level, y, x]
                
                if temp < 273.15 and (qr > 0 or qc > 0):
                    pres = p_vals[level, y, x]
                    alt_ft = pressure_to_altitude_ft(pres)
                    
                    d_bin = round(dist_on_path / 5.0) * 5.0
                    a_bin = round(alt_ft / 500.0) * 500.0
                    key = (d_bin, a_bin)
                    
                    rho = pres / (287.05 * temp)
                    lwc_gm3 = float((qr + qc) * rho * 1000.0)
                    
                    if key not in profile_hits or lwc_gm3 > profile_hits[key]["intensity"]:
                        profile_hits[key] = {
                            "dist": float(d_bin),
                            "alt_ft": float(a_bin),
                            "intensity": lwc_gm3,
                            "temp_c": float(temp - 273.15),
                            "lat": float(c_lat),
                            "lon": float(c_lon)
                        }
    
    # 6. Generar línea de vuelo
    flight_line = get_flight_profile(total_dist, target_fl=290)
    
    # Asegurar que los datos de engelamiento están ordenados por distancia para Plotly
    # Aunque Plotly maneja burbujas, el perfil de vuelo debe ser estrictamente creciente en X
    bubbles = list(profile_hits.values())
    bubbles.sort(key=lambda x: x["dist"])
    
    return {
        "status": "success",
        "route": [{"lat": float(p[0]), "lon": float(p[1]), "dist": float(d)} for p, d in zip(path_points, distances)],
        "flight_path": [{"dist": float(p[0]), "alt_ft": float(p[1])} for p in flight_line],
        "icing_bubbles": bubbles,
        "total_distance_km": float(total_dist),
        "corridor_km": float(corridor_width_km)
    }

