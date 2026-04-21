/**
 * Aviation Weather - Icing Risk Radar
 * Glassmorphism Interactive Interface
 */

class IcingRadarApp {
    constructor() {
        this.map = null;
        this.metadata = null;
        this.currentFrameIndex = 0;
        this.isPlaying = false;
        this.animationTimer = null;
        this.overlay = null;
        this.playbackSpeed = 1000; // ms per frame
        this.viewMode = 'bottom'; // Cambiado de 'top' a 'bottom' para coincidir con el estado inicial visual y los tonos azulados (Nivel Superior)

        // UI Elements
        this.playBtn = document.getElementById('playBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.timeSlider = document.getElementById('timeSlider');
        this.currentTimeDisplay = document.getElementById('currentTime');
        this.latDisplay = document.getElementById('latDisplay');
        this.lonDisplay = document.getElementById('lonDisplay');

        // Mode buttons
        this.modeTopBtn = document.getElementById('modeTopBtn');
        this.modeBottomBtn = document.getElementById('modeBottomBtn');

        // Trajectory state
        this.trajectoryMode = false;
        this.points = [];
        this.markers = [];
        this.orthoLine = null;
        
        // UI Elements for Trajectory
        this.trajectoryBtn = document.getElementById('trajectoryBtn');
        this.profilePanel = document.getElementById('profilePanel');
        this.closeProfileBtn = document.getElementById('closeProfileBtn');
        this.pointAStr = document.getElementById('pointA');
        this.pointBStr = document.getElementById('pointB');
        this.totalDistStr = document.getElementById('totalDist');

        this.init();
    }

    async init() {
        this.setupMap();
        await this.loadMetadata();
        this.setupEventListeners();
        this.showFrame(0);
    }

    setupMap() {
        // Initialize Leaflet Map
        this.map = L.map('map', {
            zoomControl: true,
            attributionControl: false,
            center: [40, -4], // Initial center (Spain approx)
            zoom: 5,
            minZoom: 4,
            maxZoom: 10
        });

        // Add Dark Matter Tile Layer (CartoDB)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(this.map);

        // Position zoom control
        this.map.zoomControl.setPosition('bottomright');
    }

    async loadMetadata() {
        try {
            const response = await fetch('../output/metadata.json');
            this.metadata = await response.json();
            
            // Configure slider
            const framesCount = this.metadata.frames_top ? this.metadata.frames_top.length : 
                              (this.metadata.frames ? this.metadata.frames.length : 0);
            this.timeSlider.max = framesCount - 1;
            
            // Focus map on data extent
            const extent = this.metadata.extent; // [minLon, maxLon, minLat, maxLat]
            const bounds = [[extent[2], extent[0]], [extent[3], extent[1]]];
            this.map.fitBounds(bounds);
            
            console.log('Metadata loaded:', this.metadata);
        } catch (error) {
            console.error('Error loading metadata:', error);
            this.currentTimeDisplay.textContent = "Error al cargar datos.";
        }
    }

    setupEventListeners() {
        this.playBtn.addEventListener('click', () => this.togglePlayback());
        this.prevBtn.addEventListener('click', () => this.prevFrame());
        this.nextBtn.addEventListener('click', () => this.nextFrame());
        
        this.modeTopBtn.addEventListener('click', () => this.setViewMode('top'));
        this.modeBottomBtn.addEventListener('click', () => this.setViewMode('bottom'));

        this.timeSlider.addEventListener('input', (e) => {
            this.stopPlayback();
            this.showFrame(parseInt(e.target.value));
            // Update profile if visible
            if (!this.profilePanel.classList.contains('hidden') && this.points.length === 2) {
                this.fetchProfile();
            }
        });

        // Trajectory toggle
        this.trajectoryBtn.addEventListener('click', () => this.toggleTrajectoryMode());
        this.closeProfileBtn.addEventListener('click', () => this.hideProfile());

        // Map clicks
        this.map.on('click', (e) => {
            if (this.trajectoryMode) {
                this.handleMapClick(e.latlng);
            }
        });

        // Mouse move - show coordinates
        this.map.on('mousemove', (e) => {
            this.latDisplay.textContent = e.latlng.lat.toFixed(2);
            this.lonDisplay.textContent = e.latlng.lng.toFixed(2);
        });

        // Preload images to avoid flickering
        window.addEventListener('load', () => this.preloadFrames());
    }

    preloadFrames() {
        if (!this.metadata) return;
        
        const topFrames = this.metadata.frames_top || [];
        const bottomFrames = this.metadata.frames_bottom || [];
        const legacyFrames = this.metadata.frames || [];
        
        topFrames.concat(bottomFrames).concat(legacyFrames).forEach(frame => {
            const img = new Image();
            img.src = `../output/${frame.file}`;
        });
    }

    setViewMode(mode) {
        if (this.viewMode === mode) return;
        this.viewMode = mode;
        
        // Update UI
        // El botón etiquetado como "Nivel Inferior" (modeTopBtn) activa el modo 'top' (mínima presión, tonos rojizos)
        // El botón etiquetado como "Nivel Superior" (modeBottomBtn) activa el modo 'bottom' (máxima presión, tonos azulados)
        if (mode === 'top') {
            this.modeTopBtn.classList.add('active');
            this.modeBottomBtn.classList.remove('active');
        } else {
            this.modeTopBtn.classList.remove('active');
            this.modeBottomBtn.classList.add('active');
        }
        
        this.showFrame(this.currentFrameIndex);
    }

    showFrame(index) {
        if (!this.metadata) return;
        
        const frames = this.viewMode === 'top' ? this.metadata.frames_top : this.metadata.frames_bottom;
        let frame = frames ? frames[index] : null;

        if (!frame) {
            // Fallback for old metadata format
            const legacyFrames = this.metadata.frames;
            if (!legacyFrames || !legacyFrames[index]) return;
            frame = legacyFrames[index];
        }

        this.updateOverlay(frame.file, index, frame.timestamp);
    }

    updateOverlay(file, index, timestamp) {
        this.currentFrameIndex = index;
        
        // Update UI
        this.timeSlider.value = index;
        this.currentTimeDisplay.textContent = this.formatTimestamp(timestamp);
        
        // Update Map Overlay
        const imageUrl = `../output/${file}`;
        const extent = this.metadata.extent;
        const imageBounds = [[extent[2], extent[0]], [extent[3], extent[1]]];

        if (this.overlay) {
            this.overlay.setUrl(imageUrl);
        } else {
            this.overlay = L.imageOverlay(imageUrl, imageBounds, {
                opacity: 0.8,
                interactive: false,
                crossOrigin: true
            }).addTo(this.map);
        }
    }

    formatTimestamp(ts) {
        // WRF format: 2015-04-17T18:00:00.000000000
        const date = new Date(ts);
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'UTC'
        }) + ' UTC';
    }

    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        this.isPlaying = true;
        this.playBtn.textContent = '⏸';
        this.playBtn.classList.add('playing');
        
        const framesCount = parseInt(this.timeSlider.max) + 1;
        this.animationTimer = setInterval(() => {
            let nextIdx = (this.currentFrameIndex + 1) % framesCount;
            this.showFrame(nextIdx);
        }, this.playbackSpeed);
    }

    stopPlayback() {
        this.isPlaying = false;
        this.playBtn.textContent = '▶';
        this.playBtn.classList.remove('playing');
        clearInterval(this.animationTimer);
    }

    nextFrame() {
        this.stopPlayback();
        const framesCount = parseInt(this.timeSlider.max) + 1;
        let nextIdx = (this.currentFrameIndex + 1) % framesCount;
        this.showFrame(nextIdx);
    }

    prevFrame() {
        this.stopPlayback();
        const framesCount = parseInt(this.timeSlider.max) + 1;
        let prevIdx = (this.currentFrameIndex - 1 + framesCount) % framesCount;
        this.showFrame(prevIdx);
    }

    // --- Trajectory Logic ---

    toggleTrajectoryMode() {
        this.trajectoryMode = !this.trajectoryMode;
        if (this.trajectoryMode) {
            this.trajectoryBtn.classList.add('active');
            this.trajectoryBtn.innerHTML = '<span class="icon">❌</span> Cancelar selección';
            this.map.getContainer().classList.add('selecting-path');
            this.clearTrajectory();
        } else {
            this.trajectoryBtn.classList.remove('active');
            this.trajectoryBtn.innerHTML = '<span class="icon">✈️</span> Perfil de trayectoria';
            this.map.getContainer().classList.remove('selecting-path');
        }
    }

    clearTrajectory() {
        this.points = [];
        this.markers.forEach(m => this.map.removeLayer(m));
        this.markers = [];
        if (this.orthoLine) {
            this.map.removeLayer(this.orthoLine);
            this.orthoLine = null;
        }
        this.hideProfile();
    }

    handleMapClick(latlng) {
        if (this.points.length >= 2) {
            this.clearTrajectory();
        }

        this.points.push(latlng);
        console.log(`Punto ${this.points.length} seleccionado:`, latlng);
        
        const label = this.points.length === 1 ? 'Salida (A)' : 'Llegada (B)';
        const marker = L.marker(latlng, {
            title: label,
            draggable: false
        }).addTo(this.map).bindTooltip(label, { 
            permanent: true, 
            direction: 'top',
            className: 'custom-marker-label'
        });
        
        this.markers.push(marker);

        if (this.points.length === 2) {
            console.log('Trayectoria completa. A:', this.points[0], 'B:', this.points[1]);
            this.fetchProfile();
            // Exit selection mode automatically
            this.toggleTrajectoryMode();
        }
    }

    async fetchProfile() {
        if (this.points.length < 2) return;

        // Mantener orden estricto A -> B
        const p1 = this.points[0]; // Salida (A)
        const p2 = this.points[1]; // Llegada (B)
        const time = this.currentFrameIndex;

        console.log(`Solicitando perfil: A(${p1.lat}, ${p1.lng}) -> B(${p2.lat}, ${p2.lng})`);

        try {
            const url = `/api/profile?lat1=${p1.lat}&lon1=${p1.lng}&lat2=${p2.lat}&lon2=${p2.lng}&time=${time}`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.status === 'success') {
                this.drawOrthodromic(data.route);
                this.showProfile(data);
            } else {
                alert('Error al calcular el perfil: ' + (data.message || 'Desconocido'));
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
            alert('Error de conexión con el servidor.');
        }
    }

    drawOrthodromic(route) {
        if (this.orthoLine) this.map.removeLayer(this.orthoLine);
        
        const latlngs = route.map(r => [r.lat, r.lon]);
        this.orthoLine = L.polyline(latlngs, {
            color: '#38bdf8',
            weight: 3,
            dashArray: '5, 10',
            opacity: 0.8
        }).addTo(this.map);
    }

    showProfile(data) {
        this.profilePanel.classList.remove('hidden');
        this.pointAStr.textContent = `${data.route[0].lat.toFixed(2)}, ${data.route[0].lon.toFixed(2)}`;
        const last = data.route[data.route.length - 1];
        this.pointBStr.textContent = `${last.lat.toFixed(2)}, ${last.lon.toFixed(2)}`;
        this.totalDistStr.textContent = data.total_distance_km.toFixed(1);

        this.renderChart(data);
    }

    hideProfile() {
        this.profilePanel.classList.add('hidden');
    }

    renderChart(data) {
        const totalDist = data.total_distance_km;
        
        // Inversión forzada del eje X para que coincida con la percepción visual del usuario
        // dist_grafica = totalDist - dist_real
        const flightX = data.flight_path.map(p => totalDist - p.dist);
        const flightY = data.flight_path.map(p => p.alt_ft);

        const bubblesX = data.icing_bubbles.map(b => totalDist - b.dist);
        const bubblesY = data.icing_bubbles.map(b => b.alt_ft);
        const bubblesIntensity = data.icing_bubbles.map(b => b.intensity);
        const bubblesText = data.icing_bubbles.map(b => `T: ${b.temp_c.toFixed(1)}°C<br>LWC: ${b.intensity.toFixed(3)} g/m³<br>Dist Origen: ${b.dist.toFixed(0)} km`);

        const traceFlight = {
            x: flightX,
            y: flightY,
            mode: 'lines',
            name: 'Trayectoria Vuelo (FL290)',
            line: { color: '#ffffff', width: 3, dash: 'solid' }
        };

        const traceIcing = {
            x: bubblesX,
            y: bubblesY,
            mode: 'markers',
            name: 'Riesgo Engelamiento (Corredor 15km)',
            text: bubblesText,
            hoverinfo: 'text',
            marker: {
                size: 8,
                color: bubblesIntensity,
                colorscale: 'YlOrRd',
                showscale: true,
                colorbar: {
                    title: 'LWC (g/m³)',
                    thickness: 15,
                    x: 1.05
                },
                opacity: 0.6,
                line: {
                    color: 'rgba(255, 255, 255, 0.1)',
                    width: 0.5
                }
            }
        };

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
            font: { color: '#f8fafc', family: 'Inter' },
            margin: { t: 30, b: 60, l: 60, r: 80 },
            hovermode: 'closest',
            xaxis: {
                title: 'Distancia recorrida (km)',
                gridcolor: 'rgba(255,255,255,0.1)',
                zeroline: false,
                autorange: true, // Asegurar que Plotly no invierta el eje
                fixedrange: false
            },
            yaxis: {
                title: 'Altitud (ft)',
                gridcolor: 'rgba(255,255,255,0.1)',
                zeroline: false,
                side: 'left',
                range: [0, 35000] // Rango fijo para altitud
            },
            yaxis2: {
                title: 'Metros / FL',
                overlaying: 'y',
                side: 'right',
                showgrid: false,
                tickmode: 'array',
                tickvals: [0, 5000, 10000, 15000, 20000, 25000, 29000, 35000],
                ticktext: ['0m', '1524m', '3048m', '4572m', '6096m', '7620m', 'FL290', '10668m']
            },
            showlegend: false
        };

        Plotly.newPlot('profileChart', [traceIcing, traceFlight], layout, { responsive: true, displayModeBar: false });
    }
}

// Start App
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IcingRadarApp();
});
