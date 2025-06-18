// Initialize map
var map = L.map('map').setView([20, 0], 2);

// Dark mode tile layer
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors & CartoDB',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Function to add attack markers and line
function addAttack(sourceCoords, destCoords, sourceCountry, destCountry, type) {
    const sourceMarker = L.circleMarker(sourceCoords, {
        radius: 8,
        color: 'lime',
        fillColor: 'lime',
        fillOpacity: 0.8,
        className: 'glow-marker'
    }).addTo(map);

    const destMarker = L.circleMarker(destCoords, {
        radius: 8,
        color: 'red',
        fillColor: 'red',
        fillOpacity: 0.8,
        className: 'glow-marker'
    }).addTo(map);

    const line = L.polyline([sourceCoords, destCoords], {
        color: '#ccc',
        weight: 2,
        opacity: 0.5
    }).addTo(map);

    logAttack(sourceCountry, destCountry, type);
    glowCountry(sourceCountry);
    glowCountry(destCountry);

    // Remove after 8 seconds
    setTimeout(() => {
        map.removeLayer(sourceMarker);
        map.removeLayer(destMarker);
        map.removeLayer(line);
    }, 8000);
}

// Log attacks in left info panel
function logAttack(source, dest, type) {
    const log = document.getElementById("attack-log");
    const item = document.createElement("li");
    item.textContent = `${type} from ${source} to ${dest}`;
    log.prepend(item);
}

// Simulate glow for country name
function glowCountry(countryName) {
    const label = document.getElementById(countryName);
    if (label) {
        label.classList.add('glow-text');
        setTimeout(() => label.classList.remove('glow-text'), 8000);
    }
}

// Example (dummy) attack every 10 seconds
setInterval(() => {
    addAttack([40.7128, -74.0060], [51.5074, -0.1278], "USA", "UK", "DDoS");
}, 10000);