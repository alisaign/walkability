function getCategoryIconClass(category) {
    const icons = {
        metro: 'fa-subway',
        bus: 'fa-bus',
        grocery: 'fa-shopping-cart',
        restaurants: 'fa-utensils',
        parks: 'fa-tree',
        schools: 'fa-graduation-cap',
        healthcare: 'fa-hospital',
    };
    return icons[category] || 'fa-map-marker-alt';
}

function initWalkabilityMap(DATA) {
    const center = [DATA.center.lat, DATA.center.lon];
    const map = L.map('map').setView(center, 15); // zoom like fallback

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    L.marker(center).addTo(map).bindPopup('Your Location');

    if (DATA.buffers_m && DATA.breakdown) {
        DATA.breakdown.forEach((item, i) => {
            if (item.weight > 0 && item.nearby_count > 0) {
                L.circle(center, {
                    radius: DATA.buffers_m[i],
                    color: '#ea580c',
                    fillColor: '#f97316',
                    weight: 1,
                    opacity: 0.3,
                    fillOpacity: 0.1
                }).addTo(map).bindPopup(`${item.name} buffer (${DATA.buffers_m[i]} m)`);

                const iconClass = getCategoryIconClass(item.name);
                const nearby = DATA.nearby.filter(poi => poi.category === item.name);
                nearby.forEach(poi => {
                    if (poi.geometry && poi.geometry.coordinates) {
                        const [lon, lat] = poi.geometry.coordinates;
                        const customIcon = L.divIcon({
                            html: `<i class="fas ${iconClass}" style="color:#f97316;font-size:18px;"></i>`,
                            className: 'custom-marker-icon',
                            iconSize: [20, 20],
                            iconAnchor: [10, 10]
                        });
                        L.marker([lat, lon], { icon: customIcon })
                            .addTo(map)
                            .bindPopup(`<strong>${poi.name || item.name}</strong><br><small>${item.name}</small>`);
                    }
                });
            }
        });
    }
}
