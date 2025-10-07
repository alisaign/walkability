function initWalkabilityMap(DATA) {
    const center = [DATA.center.lat, DATA.center.lon];
    const map = L.map('map').setView(center, 15); // zoom like fallback

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Center marker
    L.marker(center).addTo(map).bindPopup('Your Location');

    // Buffer circles – thicker & warmer like fallback
    if (DATA.buffers_m) {
        DATA.buffers_m.forEach(r => {
            L.circle(center, {
                radius: r,
                color: '#ea580c',
                fillColor: '#f97316',
                weight: 1,
                opacity: 0.3,
                fillOpacity: 0.1
            }).addTo(map);
        });
    }

    // Nearby points
    if (DATA.nearby && DATA.nearby.length > 0) {
        DATA.nearby.forEach(p => {
            if (!p.geometry || !p.geometry.coordinates) return;
            const [lon, lat] = p.geometry.coordinates;
            const name = p.name || p.category || "place";
            L.circleMarker([lat, lon], {
                radius: 6,
                fillColor: '#f97316',
                color: '#ea580c',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            })
                .addTo(map)
                .bindPopup(`<strong>${name}</strong>`);
        });
    } else {
        console.log("No nearby points returned.");
    }
}
