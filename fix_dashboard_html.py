import sys

content = open('templates/dashboard.html', 'r', encoding='utf-8').read()

old_badges = """                    <div class="map-title-row">
                        <h1 class="section-title" id="mapMainTitle">Live Tactical Map (Phone GPS)</h1>
                        <span class="route-badge" id="mapRouteHud" style="background: #ecfdf5; border-color: #a7f3d0; color: #047857;">Source: Android Phone</span>
                    </div>"""

new_badges = """                    <div class="map-title-row">
                        <h1 class="section-title" id="mapMainTitle">Live Tactical Map (Phone GPS)</h1>
                        <span class="route-badge" id="mapRouteHud" style="background: #ecfdf5; border-color: #a7f3d0; color: #047857;">Source: Android Phone</span>
                        <div style="display: flex; gap: 8px; margin-left: auto;">
                            <span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; border: 1px solid #bae6fd;">Registered Drones: {{ total_registered_drones|default:"0" }}</span>
                            <span style="background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; border: 1px solid #bbf7d0;">Currently Flying: {{ total_flying_drones|default:"0" }}</span>
                        </div>
                    </div>"""

content = content.replace(old_badges, new_badges)
open('templates/dashboard.html', 'w', encoding='utf-8').write(content)

print("Updated dashboard.html")
