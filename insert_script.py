import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's remove any existing inline scripts about toggleDropdown or selectMod first, if they exist
content = re.sub(r'<script>\s*// Mods Dropdown Logic for ATC.*?</script>', '', content, flags=re.DOTALL)

script = '''
<script>
    // State Tracking for Modes to allow Back/Forth navigation
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.mode) {
            selectMod(event.state.mode, null, true);
        } else {
            // Check hash
            if (location.hash) {
                selectMod(location.hash.replace('#', ''), null, true);
            } else {
                selectMod('test_phone', null, true);
            }
        }
    });

    function toggleDropdown(id, event) {
        if (id === 'modsDropdown' && event.target.tagName !== 'INPUT') {
            const cb = document.getElementById('hamburger-checkbox');
            if (cb) cb.checked = !cb.checked;
        }
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const el = document.getElementById(id);
        const isVisible = el.style.display === 'block';
        
        if (id === 'modsDropdown') {
            const testingDropdown = document.getElementById('testingDropdown');
            if (testingDropdown) testingDropdown.style.display = 'none';
        }
        
        el.style.display = isVisible ? 'none' : 'block';
    }

    window.onclick = function(event) {
        if (!event.target.closest('.hamburger') && !event.target.matches('.btn-outline') && !event.target.closest('.dropdown-submenu')) {
            const mods = document.getElementById('modsDropdown');
            const test = document.getElementById('testingDropdown');
            if (mods) { mods.style.display = 'none'; const cb = document.getElementById('hamburger-checkbox'); if (cb) cb.checked = false; }
            if (test) test.style.display = 'none';
        }
    }

    function selectMod(mode, event, isPopState=false) {
        if (event) event.preventDefault();
        
        const mods = document.getElementById('modsDropdown');
        const test = document.getElementById('testingDropdown');
        if (mods) { mods.style.display = 'none'; const cb = document.getElementById('hamburger-checkbox'); if (cb) cb.checked = false; }
        if (test) test.style.display = 'none';
        
        const hotspotBanner = document.getElementById('hotspotBanner');
        const esp32Banner = document.getElementById('esp32Banner');
        const telemetryGrid = document.querySelector('.telemetry-grid');
        const statusSection = document.querySelector('.status-section');
        const testerPanel = document.getElementById('testerPanel');
        
        const mapTitle = document.getElementById('mapMainTitle');
        const mapRoute = document.getElementById('mapRouteHud');
        
        if (hotspotBanner) hotspotBanner.style.display = 'none';
        if (esp32Banner) esp32Banner.style.display = 'none';
        if (telemetryGrid) telemetryGrid.style.display = 'none';
        if (statusSection) statusSection.style.display = 'none';
        if (testerPanel) testerPanel.style.display = 'none';
        
        if (window.clearMapHistory) window.clearMapHistory();
        if (mode === 'main') {
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
        } else if (mode === 'simulator') {
            if (mapTitle) mapTitle.innerText = "Simulation Mode (5 Drones)";
            if (mapRoute) mapRoute.innerText = "Simulator";
        } else if (mode === 'test_phone') {
            if (window.setDashboardMode) window.setDashboardMode('phone');
            if (mapTitle) mapTitle.innerText = "Live Tactical Map (Phone GPS)";
            if (mapRoute) mapRoute.innerText = "Source: Android Phone";
            if (hotspotBanner) hotspotBanner.style.display = 'flex';
            if (telemetryGrid) telemetryGrid.style.display = 'grid';
            if (statusSection) statusSection.style.display = 'block';
        } else if (mode === 'test_drone') {
            if (window.setDashboardMode) window.setDashboardMode('drone');
            if (mapTitle) mapTitle.innerText = "Live Tactical Map (ESP32 Drone)";
            if (mapRoute) mapRoute.innerText = "Source: Drone ESP32";
            if (esp32Banner) esp32Banner.style.display = 'flex';
            if (telemetryGrid) telemetryGrid.style.display = 'grid';
            if (statusSection) statusSection.style.display = 'block';
        }

        if (!isPopState) {
            history.pushState({mode: mode}, '', location.pathname + '#' + mode);
        }
    }

    // Initialize default view for ATC (Main Mode)
    {% if request.session.user_role == 'ATC' %}
    document.addEventListener("DOMContentLoaded", function() {
        if (location.hash) {
            const currentMode = location.hash.replace('#', '');
            selectMod(currentMode, null, true);
            history.replaceState({mode: currentMode}, '', location.pathname + '#' + currentMode);
        } else {
            selectMod('test_phone', null, true);
            history.replaceState({mode: 'test_phone'}, '', location.pathname + '#test_phone');
        }
    });
    {% endif %}
</script>
</body>
'''
content = content.replace('</body>', script)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
