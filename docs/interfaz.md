# Interfaz - Mapa Interactivo y Perfil Vertical

## 1. Vista General
La aplicación utiliza una estética **Glassmorphism** sobre un mapa base oscuro para maximizar el contraste de las zonas de riesgo.

### Componentes Principales:
- **Mapa Leaflet:** Visualización 2D del riesgo (techo y base).
- **Panel de Control:** Reproducción temporal y selector de niveles.
- **Perfil Vertical:** Gráfico interactivo (Plotly) de la sección transversal de una ruta.

---

## 2. Modos de Visualización 2D
El usuario puede alternar entre dos perspectivas del riesgo de engelamiento:

| Modo | Descripción | Visualización |
|------|-------------|---------------|
| **Nivel Inferior** | Base del engelamiento (máxima presión). | Tonos azulados (niveles bajos). |
| **Nivel Superior** | Techo del engelamiento (mínima presión). | Tonos rojizos (niveles altos). |

---

## 3. Perfil Vertical (Cross-Section)
Herramienta avanzada para la planificación de rutas aéreas.

### Características:
1. **Selección A-B:** El usuario marca dos puntos en el mapa para definir la trayectoria.
2. **Trayectoria Ortodrómica:** Cálculo automático de la ruta de gran círculo.
3. **Corredor de 15km:** El perfil no es una línea, sino un corredor de 15 km de ancho a cada lado de la ruta para considerar desviaciones o incertidumbre.
4. **Magnitud Física (LWC):** 
   - Se muestra el **Liquid Water Content ($g/m^3$)**.
   - Calculado dinámicamente: $LWC = (QRAIN + QCLOUD) \cdot \rho_{aire}$.
5. **Perfil de Vuelo:**
   - Trayectoria idealizada hasta **FL290**.
   - Fases: Ascenso (20% dist), Crucero (60% dist), Descenso (20% dist).

---

## 4. Paleta de Colores (Leyenda)
Se utiliza la escala `RdYlBu_r` para representar la altitud/presión:

| Presión (hPa) | Altitud (ft) | Color |
|---------------|--------------|-------|
| 300 | ~30,000 | Rojo (Cálido) |
| 500 | ~18,000 | Naranja |
| 700 | ~10,000 | Amarillo |
| 850 | ~5,000 | Blanco/Azul claro |
| 1000 | 0 | Azul (Frío) |

---

## 5. Requisitos Técnicos
- **Frontend:** Leaflet.js, Plotly.js, Lucide Icons.
- **Backend:** Python (http.server), xarray para procesamiento de datos WRF.
- **Comunicación:** API REST `/api/profile` que calcula perfiles bajo demanda.
