import sys

content = open('templates/dashboard.html', 'r', encoding='utf-8').read()

old_banner = """        <!-- PILOT UNREGISTERED/UNVERIFIED DRONE BANNER -->
        {% if request.session.user_role == 'PILOT' %}
        <div class="hotspot-info-card" style="background-color: #fef2f2; border-color: #fca5a5; display: flex; align-items: center; justify-content: flex-start; padding: 1rem 1.25rem;">
            <div class="hotspot-icon" style="background: #fee2e2; color: #dc2626; flex-shrink: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            </div>
            <div style="margin-left: 1rem;">
                <div class="hotspot-text-title" style="color: #991b1b; font-size: 1.05rem;">Registration is not complete</div>
                <div class="hotspot-text-sub" style="color: #b91c1c; font-size: 0.9rem; margin-top: 4px;">
                    Your drone registration or verification status is pending. Please <a href="{% url 'telemetry:under_construction' %}" style="text-decoration: underline; font-weight: 600;">go and register your drone</a> to gain full access.
                </div>
            </div>
        </div>
        {% endif %}"""

# Remove the banner from its current position
content = content.replace(old_banner, "")

# Find the start of the map container
map_start = '<div id="map" class="map-container"'

# We will wrap the map div inside a position:relative container, and overlay if PILOT and not complete.
# Wait, actually we can just put an overlay div inside the map-section but above the map container.
new_map_start = """        <!-- PILOT UNREGISTERED OVERLAY -->
        {% if request.session.user_role == 'PILOT' and not is_fully_registered %}
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.9); z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
            <div style="background-color: #fef2f2; border: 2px solid #fca5a5; border-radius: 12px; padding: 3rem; text-align: center; max-width: 500px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);">
                <div style="background: #fee2e2; color: #dc2626; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border-radius: 50%; margin: 0 auto 1.5rem;">
                    <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h2 style="color: #991b1b; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Registration Incomplete</h2>
                <p style="color: #b91c1c; font-size: 1rem; line-height: 1.5; margin-bottom: 2rem;">
                    Your profile or drone registration is still pending. You cannot access the live tactical map until your status is approved by the ATC Administrator.
                </p>
                <a href="{% url 'telemetry:status' %}" style="display: inline-block; background: #dc2626; color: white; padding: 0.75rem 2rem; border-radius: 6px; font-weight: 600; text-decoration: none; transition: background 0.2s;">Go to Status Page</a>
            </div>
        </div>
        {% endif %}
        
        <div id="map" class="map-container" style="position: relative;" """

content = content.replace('<div id="map" class="map-container"', new_map_start)

# In order for position: absolute to work perfectly, we need to ensure map-section is position: relative
content = content.replace('<section class="map-section" aria-label="Interactive Map">', '<section class="map-section" aria-label="Interactive Map" style="position: relative;">')

open('templates/dashboard.html', 'w', encoding='utf-8').write(content)
print("Updated dashboard.html with map overlay")
