import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the ATC condition before hotspotBanner
content = content.replace('<div class="hotspot-info-card" id="hotspotBanner">', 
'''{% if request.session.user_role == 'ATC' %}
        <div class="hotspot-info-card" id="hotspotBanner">''')

# Add the closing endif after esp32Banner
content = content.replace('''            <div class="connection-banner-actions">
                <div id="esp32WsStatusBadge" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;">
                    <span class="status-indicator-dot dot-red" id="esp32WsDot"></span>
                    <span id="esp32WsStatusText">ESP32 Offline</span>
                </div>
            </div>
        </div>''', '''            <div class="connection-banner-actions">
                <div id="esp32WsStatusBadge" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;">
                    <span class="status-indicator-dot dot-red" id="esp32WsDot"></span>
                    <span id="esp32WsStatusText">ESP32 Offline</span>
                </div>
            </div>
        </div>
        {% endif %}''')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
