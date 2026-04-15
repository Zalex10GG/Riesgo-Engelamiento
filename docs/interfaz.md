# Interfaz - Mapa Interactivo de Engelamiento

## 1. Vista General

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════════════╗  │
│  ║     MAPA INTERACTIVO DE RIESGO DE ENGELAMIENTO                    ║  │
│  ║     (Barra de titulo con estilo moderno)                         ║  │
│  ╚═══════════════════════════════════════════════════════════════════╝  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                                                                 │  │
│  │                    MAPA BASE (OpenStreetMap)                    │  │
│  │                      con riesgo superpuesto                     │  │
│  │                    (transparente, color RdYlBu_r)               │  │
│  │                                                                 │  │
│  │         [Zona de riesgo de engelamiento]                         │  │
│  │              con contornos suavizados                            │  │
│  │                                                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ───────────────────────────────────────────────────────────────────  │
│                                                                         │
│  CONTROLES TEMPORALES:                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  [▶ Play] [⏸ Pause]    ◄ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ►     │  │
│  │              Slider temporal (11 timesteps)                   │  │
│  │ Hora: 2015-04-17 19:00 UTC                                   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ───────────────────────────────────────────────────────────────────  │
│                                                                         │
│  LEYENDA:                                                             │
│  ┌──────────────────────────┐                                        │
│  │ Alta (>950 hPa) │ Nieve │                                        │
│  │        ...             │                                        │
│  │ Baja (<850 hPa) │ Rojo │                                        │
│  │ Presión (hPa)         │                                        │
│  └──────────────────────────┘                                        │
│                                                                         │
│  INFO PANEL (esquina inferior derecha):                                │
│  - Timestamp actual                                                   │
│  - Puntos de riesgo: 21,074                                          │
│  - Área afectada: ~2,500 km²                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Paleta de Colores

### Mapa de Riesgo (RdYlBu_r - invertida)
| Presión (hPa) | Color | Significado |
|---------------|-------|-------------|
| > 950 | Blanco/Nieve | Baja altitud (cerca del suelo) |
| 900 - 950 | Azul claro | Altitud media-baja |
| 870 - 900 | Azul | Altitud media |
| 850 - 870 | Rojo | Alta altitud |
| < 850 | Rojo oscuro | Muy alta altitud |

### Fondo del Mapa
- **OpenStreetMap** contileserver (estándar de Plotly)
- Alternativa: CartoDB Dark Matter (más contraste)

---

## 3. Componentes UI

### 3.1 Barra de Título
- Fondo: `#1a1a2e` (azul muy oscuro)
- Texto: `#ffffff` (blanco)
- Fuente: Roboto, 18px, bold
- Padding: 15px

### 3.2 Controles de Reproducción
- Botones: Circulares, fondo `#e94560` (rojo/coral)
- Hover: `#ff6b6b`
- Iconos: ▶ Play, ⏸ Pause
- Tamaño: 40x40px

### 3.3 Slider Temporal
- Track: `#e0e0e0` (gris claro)
- Fill: `#e94560` (rojo/coral)
- Thumb: `#1a1a2e` (azul oscuro), 16px
- Etiquetas: Fechas en formato `YYYY-MM-DD HH:MM`

### 3.4 Leyenda (Colorbar)
- Posición: Derecha del mapa
- Ancho: 80px
- Título: "Presión (hPa)"
- Tick labels: 10px

### 3.5 Panel de Información
- Fondo: `rgba(26, 26, 46, 0.9)` (semi-transparente)
- Texto: `#ffffff`
- Posición: Esquina inferior derecha
- Shows: Timestamp, Puntos de riesgo, Área

---

## 4. Estilos CSS Custom

```css
/* Contenedor principal */
.plotly-main-div {
    font-family: 'Roboto', sans-serif;
    background: #f5f5f5;
}

/* Título */
.nice-title {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #ffffff;
    padding: 15px 20px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

/* Botones de control */
.js-plotly-plot .plotly .modebar-btn {
    background: #e94560 !important;
    color: #ffffff !important;
    border-radius: 50%;
    width: 36px;
    height: 36px;
}

.js-plotly-plot .plotly .modebar-btn:hover {
    background: #ff6b6b !important;
}

/* Slider */
.slider {
    -webkit-slider-thumb: {
        background: #1a1a2e;
        border: 2px solid #e94560;
    }
}

/* Colorbar */
.colorbar {
    font-size: 12px;
}
```

---

## 5. Layout Responsive

### Desktop (>1200px)
- Mapa: 100% ancho, 700px alto
- Controles: Debajo del mapa
- Panel info: Fijo

### Tablet (768-1200px)
- Mapa: 100% ancho, 600px alto
- Controles: Debajo del mapa
- Panel info: Collapsible

### Móvil (<768px)
- Mapa: 100% ancho, 400px alto
- Controles: Debajo, más grandes
- Panel info: Oculto por defecto

---

## 6. Funcionalidades Interactivas

### Hover
- Tooltip mostrando: Presión, Lat/Lon, Temperatura
- Fondo: `#1a1a2e` con 90% opacidad
- Texto: Blanco

### Click
- Zoom al área seleccionada
- Popup con detalles

### Animación
- Duración frame: 500ms
- Transición: 300ms ease-in-out
- Loop: Opcional (checkbox)

---

## 7. Capas del Mapa

### Capa 1: Fondo (Base)
- OpenStreetMap tiles
- URL: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- Attribution: © OpenStreetMap contributors

### Capa 2: Riesgo (Overlay)
- Contornosfill (contourf)
- Opacidad: 70%
- Modo Blend: multiply

### Capa 3: Líneas de costa
- GeoJSON de naturalearth
- Grosor: 1px
- Color: `#333333`

---

## 8. Accesibilidad

- Contraste: Ratio > 4.5:1
- Textos: Legibles desde 14px
- Colores: No depender solo del color
- Teclado: Navegación completa