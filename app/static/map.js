function initWalkabilityMap(DATA) {
    const center = [DATA.center.lat, DATA.center.lon];
    const map = L.map('map').setView(center, 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    L.marker(center).addTo(map).bindPopup('Origin').openPopup();
    //(DATA.buffers_m || []).forEach(r => L.circle(center, { radius: r }).addTo(map));

    // 🔹 Load all transit stops (for now display everything)
    fetch('/data/processed/metro_bus_clean.geojson')
        .then(r => r.json())
        .then(geojson => {
            L.geoJSON(geojson, {
                pointToLayer: (f, latlng) =>
                    L.circleMarker(latlng, {
                        radius: 4,
                        color: '#ff0000',
                        fillColor: '#ff0000',
                        fillOpacity: 0.8
                    }).bindPopup(f.properties.stop_name)
            }).addTo(map);
        })
        .catch(err => console.error('Failed to load GeoJSON:', err));
}
  