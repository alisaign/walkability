function initWalkabilityMap(DATA) {
    const center = [DATA.center.lat, DATA.center.lon];
    const map = L.map('map').setView(center, 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    L.marker(center).addTo(map).bindPopup('Origin').openPopup();
    (DATA.buffers_m || []).forEach(r => L.circle(center, { radius: r }).addTo(map));
}
  