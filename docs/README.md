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

El sistema permite visualizar dos niveles críticos:
- **Nivel Superior (Techo):** Nivel de menor presión (mayor altitud) con riesgo.
- **Nivel Inferior (Base):** Nivel de mayor presión (menor altitud) con riesgo.

## Características de la Interfaz Web

- **Mapa Interactivo:** Visualización de frames temporales de engelamiento con Leaflet.
- **Perfil Vertical de Trayectoria:**
    - Selección de ruta ortodrómica entre dos puntos (A-B).
    - Muestreo en un corredor de 15 km de ancho.
    - Perfil de vuelo idealizado (FL290) con fases de ascenso, crucero y descenso.
    - Visualización de Liquid Water Content (LWC) en $g/m^3$.
- **Control Temporal:** Timeline interactivo para explorar la evolución del riesgo.

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
