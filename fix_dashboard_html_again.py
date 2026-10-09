import sys

content = open('templates/dashboard.html', 'r', encoding='utf-8').read()

# Fix 1: Remove " (Overview)" from the title and route badge in main mode
old_main_mode = """        if (mode === 'main') {
            if (window.setDashboardMode) window.setDashboardMode('main');
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
        }"""
new_main_mode = """        if (mode === 'main') {
            if (window.setDashboardMode) window.setDashboardMode('main');
            if (mapTitle) mapTitle.innerText = "Main Mode";
            if (mapRoute) mapRoute.innerText = "Overview";
            if (telemetryGrid) telemetryGrid.style.display = 'grid';
        }"""
content = content.replace(old_main_mode, new_main_mode)

# Add telemetryGrid to test_drone too
old_test_drone = """        } else if (mode === 'test_drone') {
            if (window.setDashboardMode) window.setDashboardMode('drone');
            if (mapTitle) mapTitle.innerText = "Live Tactical Map (ESP32 Drone)";
            if (mapRoute) mapRoute.innerText = "Source: Hardware Stream";
            if (esp32Banner) esp32Banner.style.display = 'flex';
            if (statusSection) statusSection.style.display = 'block';
        }"""
new_test_drone = """        } else if (mode === 'test_drone') {
            if (window.setDashboardMode) window.setDashboardMode('drone');
            if (mapTitle) mapTitle.innerText = "Live Tactical Map (ESP32 Drone)";
            if (mapRoute) mapRoute.innerText = "Source: Hardware Stream";
            if (esp32Banner) esp32Banner.style.display = 'flex';
            if (telemetryGrid) telemetryGrid.style.display = 'grid';
            if (statusSection) statusSection.style.display = 'block';
        }"""
content = content.replace(old_test_drone, new_test_drone)

# Add telemetryGrid to simulator too
old_simulator = """        } else if (mode === 'simulator') {
            if (window.setDashboardMode) window.setDashboardMode('simulator');
            if (mapTitle) mapTitle.innerText = "Simulation Mode (5 Drones)";
            if (mapRoute) mapRoute.innerText = "Simulator";
            if (statusSection) statusSection.style.display = 'block';
            if (window.startSimulator) window.startSimulator();
        }"""
new_simulator = """        } else if (mode === 'simulator') {
            if (window.setDashboardMode) window.setDashboardMode('simulator');
            if (mapTitle) mapTitle.innerText = "Simulation Mode (5 Drones)";
            if (mapRoute) mapRoute.innerText = "Simulator";
            if (telemetryGrid) telemetryGrid.style.display = 'grid';
            if (statusSection) statusSection.style.display = 'block';
            if (window.startSimulator) window.startSimulator();
        }"""
content = content.replace(old_simulator, new_simulator)


# Fix 2: Move registered/flying drones out of the map title area
old_counters = """                        <div style="display: flex; gap: 8px; margin-left: auto;">
                            <span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; border: 1px solid #bae6fd;">Registered Drones: {{ total_registered_drones|default:"0" }}</span>
                            <span style="background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; border: 1px solid #bbf7d0;">Currently Flying: {{ total_flying_drones|default:"0" }}</span>
                        </div>"""
content = content.replace(old_counters, "")

# Insert counters before the MAP SECTION
new_counters_section = """
        <!-- GLOBAL STATS (OUTSIDE MAIN MAP BOX) -->
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; padding: 0 1rem;">
            <div style="background: #e0f2fe; color: #0369a1; padding: 0.75rem 1.25rem; border-radius: 8px; font-size: 0.95rem; font-weight: 700; border: 1px solid #bae6fd; display: flex; align-items: center; gap: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                Registered Drones: {{ total_registered_drones|default:"0" }}
            </div>
            <div style="background: #dcfce7; color: #15803d; padding: 0.75rem 1.25rem; border-radius: 8px; font-size: 0.95rem; font-weight: 700; border: 1px solid #bbf7d0; display: flex; align-items: center; gap: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                Currently Flying: {{ total_flying_drones|default:"0" }}
            </div>
        </div>
"""

content = content.replace("<!-- MAP SECTION (LARGEST SECTION) -->", new_counters_section + "\n        <!-- MAP SECTION (LARGEST SECTION) -->")


open('templates/dashboard.html', 'w', encoding='utf-8').write(content)
print("Updated dashboard.html with fixes")
