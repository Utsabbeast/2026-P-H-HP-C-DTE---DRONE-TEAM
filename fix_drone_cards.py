import sys

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

old_drone_update_cards = """        // Update Cards
        if (elements.valLatitude) elements.valLatitude.textContent = `${lat.toFixed(6)}°`;
        if (elements.subLatitude) elements.subLatitude.textContent = lat >= 0 ? `North (+${lat.toFixed(6)})` : `South (${lat.toFixed(6)})`;
        if (elements.valLongitude) elements.valLongitude.textContent = `${lon.toFixed(6)}°`;
        if (elements.subLongitude) elements.subLongitude.textContent = lon >= 0 ? `East (+${lon.toFixed(6)})` : `West (${lon.toFixed(6)})`;
        if (elements.valAltitude) elements.valAltitude.textContent = `${alt.toFixed(1)} m`;
        if (elements.subAltitude) elements.subAltitude.textContent = 'AGL Altitude';
        if (elements.valHeading) elements.valHeading.textContent = `${Math.round(hdg)}°`;
        if (elements.subHeading) elements.subHeading.textContent = headingToCardinal(hdg);
        if (elements.compassNeedle) elements.compassNeedle.style.transform = `rotate(${hdg}deg)`;
        if (elements.valSpeed) elements.valSpeed.textContent = spdText;
        if (elements.subSpeed) elements.subSpeed.textContent = spdKmText;
        if (elements.valAccuracy) elements.valAccuracy.innerHTML = '<span style="color: #10b981; font-weight: 700;">Cube GNSS</span>';
        if (elements.subAccuracy) elements.subAccuracy.textContent = 'Hardware Telemetry (UART2)';
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;"""

new_drone_update_cards = """        // Update Cards using unified generic function
        updateTelemetryCards(telemetryData);
        if (elements.valLastUpdate) elements.valLastUpdate.textContent = timeStr;"""

content = content.replace(old_drone_update_cards, new_drone_update_cards)

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Replaced updateDroneUI card updates")
