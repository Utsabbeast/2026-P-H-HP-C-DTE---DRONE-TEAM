import sys

content = open('templates/dashboard.html', 'r', encoding='utf-8').read()

# 1. Boxier Global Stats (Registered Drones & Currently Flying)
old_stats = """        <!-- GLOBAL STATS (OUTSIDE MAIN MAP BOX) -->
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; padding: 0 1rem;">
            <div style="background: #e0f2fe; color: #0369a1; padding: 0.75rem 1.25rem; border-radius: 8px; font-size: 0.95rem; font-weight: 700; border: 1px solid #bae6fd; display: flex; align-items: center; gap: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                Registered Drones: {{ total_registered_drones|default:"0" }}
            </div>
            <div style="background: #dcfce7; color: #15803d; padding: 0.75rem 1.25rem; border-radius: 8px; font-size: 0.95rem; font-weight: 700; border: 1px solid #bbf7d0; display: flex; align-items: center; gap: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                Currently Flying: {{ total_flying_drones|default:"0" }}
            </div>
        </div>"""

new_stats = """        <!-- GLOBAL STATS (OUTSIDE MAIN MAP BOX) -->
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; padding: 0 1rem;">
            <div style="background: #002D74; color: #ffffff; padding: 0.85rem 1.5rem; border-radius: 0; font-size: 0.95rem; font-weight: 700; border: 2px solid #001A4A; display: flex; align-items: center; gap: 10px; box-shadow: 4px 4px 0px rgba(0,0,0,0.1);">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                REGISTERED DRONES: {{ total_registered_drones|default:"0" }}
            </div>
            <div style="background: #0ea5e9; color: #ffffff; padding: 0.85rem 1.5rem; border-radius: 0; font-size: 0.95rem; font-weight: 700; border: 2px solid #0284c7; display: flex; align-items: center; gap: 10px; box-shadow: 4px 4px 0px rgba(0,0,0,0.1);">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                DRONES IN AIR: {{ total_flying_drones|default:"0" }}
            </div>
        </div>"""

content = content.replace(old_stats, new_stats)

# 2. Hide telemetry-grid for guests
old_telemetry_grid = """        <!-- ----------------------------------------------------------- -->
        <!-- LIVE TELEMETRY CARDS (BOTTOM)                               -->
        <!-- ----------------------------------------------------------- -->
        <section class="telemetry-grid" aria-label="Live Telemetry Metrics">"""

new_telemetry_grid = """        <!-- ----------------------------------------------------------- -->
        <!-- LIVE TELEMETRY CARDS (BOTTOM)                               -->
        <!-- ----------------------------------------------------------- -->
        {% if request.session.user_role != 'GUEST' and request.user.username != 'guest' %}
        <section class="telemetry-grid" aria-label="Live Telemetry Metrics">"""

content = content.replace(old_telemetry_grid, new_telemetry_grid)

# We need to find the closing </section> of telemetry-grid to close the {% endif %}
old_telemetry_end = """                </div>
            </div>
        </section>"""

new_telemetry_end = """                </div>
            </div>
        </section>
        {% endif %}"""

content = content.replace(old_telemetry_end, new_telemetry_end)

open('templates/dashboard.html', 'w', encoding='utf-8').write(content)
print("Updated dashboard.html layout")
