function initWalkabilityMap(DATA) {
    const center = [DATA.center.lat, DATA.center.lon];
    const map = L.map('map').setView(center, 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // --- show user location ---
    L.marker(center).addTo(map).bindPopup('Origin').openPopup();

    // --- optional radius circles ---
    (DATA.buffers_m || []).forEach(r =>
        L.circle(center, { radius: r, color: '#0ea5e9', fillOpacity: 0.05 }).addTo(map)
    );

    // --- display nearby POIs (from backend) ---
    if (DATA.nearby && DATA.nearby.length > 0) {
        DATA.nearby.forEach(p => {
            if (!p.geometry || !p.geometry.coordinates) return;
            const [lon, lat] = p.geometry.coordinates;
            const cat = p.category || "place";
            const name = p.stop_name || p.name || cat;
            L.circleMarker([lat, lon], {
                radius: 5,
                color: "#ff0000",
                fillColor: "#ff0000",
                fillOpacity: 0.8
            }).bindPopup(`<strong>${name}</strong><br><small>${cat}</small>`).addTo(map);
        });
    } else {
        console.log("No nearby points returned.");
    }
}
