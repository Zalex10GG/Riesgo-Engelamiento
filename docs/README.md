# Engelamiento - Riesgo de Engelamiento en Aeronaves

> Detección y visualización de zonas con riesgo de engelamiento en aeronaves usando datos del modelo WRF.

## Uso

```bash
uv sync
uv run main.py
```

Los resultados se guardan en `output/`.

## Requisitos de los Datos

El archivo de entrada debe llamarse:
```
wrfout_d01_2015-04-17_18_00_00_corte.nc
```

Y estar en formato NetCDF (`.nc`) con las siguientes variables:

| Variable | Descripción |
|----------|-------------|
| `TK` | Temperatura en Kelvin |
| `QRAIN` | Proporción de mezcla de agua de lluvia |
| `QCLOUD` | Proporción de mezcla de agua de nube |
| `P` + `PB` | Presión total (perturbación + base) |
| `XLAT` | Latitud |
| `XLONG` | Longitud |

## Algoritmo de Detección

Un pixel tiene riesgo de engelamiento cuando:

1. `TK < 273.15 K` (temperatura bajo cero)
2. (`QRAIN > 0` OR `QCLOUD > 0`) (presencia de hidrometeoros líquidos)

El color en el mapa indica la presión (hPa) del nivel donde se produce engelamiento. Si hay múltiples niveles, se toma el de menor presión (mayor altitud).

## Tests

```bash
uv run pytest
```

## Estructura del Proyecto

```
engelamiento/
├── main.py              # Punto de entrada
├── src/engelamiento/    # Paquete principal
│   ├── data/            # Cargador de datos NetCDF (xarray lazy loading)
│   ├── detection/       # Lógica de detección de engelamiento
│   └── visualization/  # Generación de mapas (cartopy)
├── static/              # CSS, JS para web interactiva
├── templates/           # Plantillas HTML
├── tests/               # Tests unitarios
├── Data/                # Datos NetCDF
├── resources/           # Documentación y recursos
├── docs/                # Especificación y documentación
└── output/              # Mapas generados
```

## Autores

- Alejandro Gil Getino - agilge00@estudiantes.unileon.es
- Guillermo Alba Buitrón - galbab00@estudiantes.unileon.es
