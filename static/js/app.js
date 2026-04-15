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

        // UI Elements
        this.playBtn = document.getElementById('playBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.timeSlider = document.getElementById('timeSlider');
        this.currentTimeDisplay = document.getElementById('currentTime');
        this.latDisplay = document.getElementById('latDisplay');
        this.lonDisplay = document.getElementById('lonDisplay');

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
            this.timeSlider.max = this.metadata.frames.length - 1;
            
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
        
        this.timeSlider.addEventListener('input', (e) => {
            this.stopPlayback();
            this.showFrame(parseInt(e.target.value));
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
        this.metadata.frames.forEach(frame => {
            const img = new Image();
            img.src = `../output/${frame.file}`;
        });
    }

    showFrame(index) {
        if (!this.metadata) return;
        
        const frame = this.metadata.frames[index];
        this.currentFrameIndex = index;
        
        // Update UI
        this.timeSlider.value = index;
        this.currentTimeDisplay.textContent = this.formatTimestamp(frame.timestamp);
        
        // Update Map Overlay
        const imageUrl = `../output/${frame.file}`;
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
        
        this.animationTimer = setInterval(() => {
            let nextIdx = this.currentFrameIndex + 1;
            if (nextIdx >= this.metadata.frames.length) {
                nextIdx = 0; // Loop
            }
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
        let nextIdx = this.currentFrameIndex + 1;
        if (nextIdx < this.metadata.frames.length) {
            this.showFrame(nextIdx);
        }
    }

    prevFrame() {
        this.stopPlayback();
        let prevIdx = this.currentFrameIndex - 1;
        if (prevIdx >= 0) {
            this.showFrame(prevIdx);
        }
    }
}

// Start App
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IcingRadarApp();
});
