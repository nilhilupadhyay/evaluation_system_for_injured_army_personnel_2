// scripts.js

document.addEventListener('DOMContentLoaded', function () {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
});

function showPosition(position) {
    var latitudeField = document.getElementById('latitude');
    var longitudeField = document.getElementById('longitude');
    
    if (latitudeField && longitudeField) {
        latitudeField.value = position.coords.latitude;
        longitudeField.value = position.coords.longitude;
    }
}
