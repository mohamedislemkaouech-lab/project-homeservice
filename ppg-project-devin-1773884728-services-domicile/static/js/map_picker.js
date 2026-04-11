/**
 * Interactive Map Picker using Leaflet.js + OpenStreetMap + Nominatim
 * Reusable component for address selection with geocoding
 */
class MapPicker {
    constructor(options = {}) {
        this.mapContainer = options.mapContainer || 'map';
        this.latField = options.latField || 'latitude';
        this.lonField = options.lonField || 'longitude';
        this.addressField = options.addressField || 'address';
        this.cityField = options.cityField || null;
        this.addressDisplayField = options.addressDisplayField || 'address_display';
        this.locateButton = options.locateButton || 'locate-btn';
        this.defaultLat = options.defaultLat || 33.8869; // Tunisia center
        this.defaultLon = options.defaultLon || 9.5375;
        this.defaultZoom = options.defaultZoom || 7;
        this.height = options.height || '350px';
        
        this.map = null;
        this.marker = null;
        this.currentLat = options.initialLat || this.defaultLat;
        this.currentLon = options.initialLon || this.defaultLon;
        
        this.init();
    }
    
    init() {
        // Initialize map
        this.map = L.map(this.mapContainer).setView([this.currentLat, this.currentLon], this.defaultZoom);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Add initial marker with custom icon
        this.marker = L.marker([this.currentLat, this.currentLon], {
            draggable: true
        }).addTo(this.map);
        
        // Map click handler
        this.map.on('click', (e) => {
            this.setMarker(e.latlng.lat, e.latlng.lng);
        });
        
        // Marker drag handler
        this.marker.on('dragend', (e) => {
            const position = e.target.getLatLng();
            this.setMarker(position.lat, position.lng);
        });
        
        // Locate button handler
        const locateBtn = document.getElementById(this.locateButton);
        if (locateBtn) {
            locateBtn.addEventListener('click', () => this.locateUser());
        }
        
        // Initial reverse geocoding if coordinates exist
        if (this.currentLat !== this.defaultLat || this.currentLon !== this.defaultLon) {
            this.reverseGeocode(this.currentLat, this.currentLon);
        }
        
        // Add custom styling to map container
        const mapElement = document.getElementById(this.mapContainer);
        if (mapElement) {
            mapElement.style.borderRadius = '12px';
        }
    }
    
    setMarker(lat, lon) {
        this.currentLat = lat;
        this.currentLon = lon;
        
        // Update marker position
        this.marker.setLatLng([lat, lon]);
        
        // Update hidden fields
        const latField = document.getElementById(this.latField);
        const lonField = document.getElementById(this.lonField);
        
        if (latField) latField.value = lat.toFixed(6);
        if (lonField) lonField.value = lon.toFixed(6);
        
        // Reverse geocode to get address
        this.reverseGeocode(lat, lon);
    }
    
    locateUser() {
        if (!navigator.geolocation) {
            alert('La géolocalisation n\'est pas supportée par votre navigateur.');
            return;
        }
        
        const locateBtn = document.getElementById(this.locateButton);
        if (locateBtn) {
            locateBtn.disabled = true;
            locateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Recherche...';
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                this.map.setView([lat, lon], 13);
                this.setMarker(lat, lon);
                
                if (locateBtn) {
                    locateBtn.disabled = false;
                    locateBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Me localiser';
                }
            },
            (error) => {
                let message = 'Impossible d\'obtenir votre position.';
                if (error.code === error.PERMISSION_DENIED) {
                    message = 'Permission refusée. Veuillez autoriser l\'accès à votre position.';
                } else if (error.code === error.TIMEOUT) {
                    message = 'Délai expiré. Veuillez réessayer.';
                }
                alert(message);
                
                if (locateBtn) {
                    locateBtn.disabled = false;
                    locateBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Me localiser';
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }
    
    async reverseGeocode(lat, lon) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=fr`);
            const data = await response.json();
            
            if (data && data.display_name) {
                // Update address display field
                const addressDisplayField = document.getElementById(this.addressDisplayField);
                if (addressDisplayField) {
                    addressDisplayField.value = data.display_name;
                }
                
                // Extract city/town for city field
                if (this.cityField) {
                    const cityField = document.getElementById(this.cityField);
                    if (cityField) {
                        const city = data.address.city || data.address.town || data.address.village || data.address.county || '';
                        cityField.value = city;
                    }
                }
                
                // Update main address field if specified
                if (this.addressField && this.addressField !== this.addressDisplayField) {
                    const addressField = document.getElementById(this.addressField);
                    if (addressField) {
                        addressField.value = data.display_name;
                    }
                }
            }
        } catch (error) {
            console.error('Reverse geocoding failed:', error);
        }
    }
}

// Global function to initialize map picker (called from templates)
function initMapPicker(options) {
    return new MapPicker(options);
}
