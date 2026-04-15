# Especificación: Mapa de Riesgo de Engelamiento

> **Objetivo:** Generar un mapa radar-style que visualice los pixeles con riesgo de engelamiento basado en datos WRF.

## Requisitos Funcionales

### RF1: Detección de Engelamiento
- Un pixel tiene riesgo de engelamiento cuando:
  - `TK < 273.15 K` (temperatura bajo cero)
  - (`QRAIN > 0` OR `QCLOUD > 0`) (hidrometeoros líquidos presentes)
- Implementación lazy: cargar solo el timestep necesario

### RF2: Visualización Radar-Style
- Mapa geográfico usando `cartopy`
- Representar TODA la extensión espacial del dataset (aunque quede zona sin datos)
- Color = presión (hPa) del nivel donde se produce engelamiento
- Si hay múltiples niveles con engelamiento, tomar el de menor presión (mayor altitud)
- Suavizado entre pixeles (interpolación visual)

### RF3: Primera Iteración
- Un solo timestep fijo (hardcoded o primer índice)
- Output: imagen estática PNG

## Datos

| Variable | Dimensiones | Descripción |
|----------|-------------|-------------|
| `TK` | (Time, bottom_top, south_north, west_east) | Temperatura en Kelvin |
| `P` | (Time, bottom_top, south_north, west_east) | Presión perturbación (Pa) |
| `PB` | (Time, bottom_top, south_north, west_east) | Presión base (Pa) |
| `XLAT` | (Time, south_north, west_east) | Latitud |
| `XLONG` | (Time, south_north, west_east) | Longitud |
| `QRAIN` | (Time, bottom_top, south_north, west_east) | Agua lluvia |
| `QCLOUD` | (Time, bottom_top, south_north, west_east) | Agua nube |

Presión total = P + PB

## Arquitectura (SRE en Python)

```
engelamiento/
├── pyproject.toml
├── src/
│   └── engelamiento/
│       ├── __init__.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── loader.py          # Carga lazy del NetCDF
│       ├── detection/
│       │   ├── __init__.py
│       │   └── engelamiento.py     # Lógica de detección
│       └── visualization/
│           ├── __init__.py
│           └── radar_map.py       # Plotting con cartopy
├── main.py                        # Punto de entrada
└── output/                        # PNG output
```

## Decisiones de Diseño

1. **Lazy loading**: `xarray` con `chunks={'Time': 1}` para cargar solo timestep activo
2. **Paquetes**: `xarray`, `numpy`, `matplotlib`, `cartopy`
3. **Colorbar**: Escala de presiones (hPa), azul para alta presión (baja altitud) → rojo para baja presión (alta altitud)
4. **Interpolación**: Usar `pcolormesh` con shading para suavizado visual

## Iteraciones

- **Iteración 1 (actual)**: Un timestep fijo, output PNG estático
- **Iteración 2**: Selector de timestep (slider/ dropdown)
