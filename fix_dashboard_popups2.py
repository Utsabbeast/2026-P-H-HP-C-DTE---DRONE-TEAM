import sys
import re

content = open('static/js/dashboard.js', 'r', encoding='utf-8').read()

# Replace phone marker popup
old_phone = """        phoneMarker.bindPopup(`
            <strong style="color: #0369a1; font-family:'Outfit'">📱 Android Phone</strong><br>
            Simulating movement data
        `);"""
new_phone = """        let phoneInfo = {
            name: 'Test Phone Tracker',
            uin: 'PHONE-TEST-100',
            owner: 'System Tester',
            purpose: 'Dashboard GPS Testing',
            duration: 'Continuous',
            status: 'ACTIVE',
            color: '#10b981'
        };
        phoneMarker.bindPopup(generateDronePopup(phoneInfo));
        phoneMarker.on('click', function() {
            activeTelemetryTargetId = 'phone';
        });"""
content = content.replace(old_phone, new_phone)

# Replace drone marker popup
old_drone = """        droneMarker.bindPopup(`
            <strong style="color: #047857; font-family:'Outfit'">🛸 ESP32 Hardware</strong><br>
            Awaiting live telemetry
        `);"""
new_drone = """        let hwDroneInfo = {
            name: 'ESP32 Hardware Drone',
            uin: 'HW-ESP-001',
            owner: 'Hardware Tester',
            purpose: 'Live MAVLink Streaming',
            duration: 'Active Session',
            status: 'ACTIVE',
            color: '#0ea5e9'
        };
        droneMarker.bindPopup(generateDronePopup(hwDroneInfo));
        droneMarker.on('click', function() {
            activeTelemetryTargetId = 'hw_drone';
        });"""
content = content.replace(old_drone, new_drone)

open('static/js/dashboard.js', 'w', encoding='utf-8').write(content)
print("Updated initial markers popups")
