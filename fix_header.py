import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_header = '''    <!-- TOP NAVIGATION BAR -->
    <header class="navbar" role="banner">
        <div class="nav-container" style="position: relative; display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 1rem;">
            
            <!-- LEFT CORNER -->
            <div class="nav-left" style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                {% if request.session.user_role == 'GUEST' or request.user.username == 'guest' %}
                <a href="{% url 'telemetry:login' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; font-weight: 700; color: #002D74; border-color: #002D74; border-radius: 0;">&larr; Back</a>
                {% elif request.session.user_role == 'PILOT' %}
                <a href="{% url 'telemetry:under_construction' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; border-radius: 0; color: #002D74; border-color: #002D74; font-weight: 700;">Profile</a>
                <a href="{% url 'telemetry:status' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; border-radius: 0; color: #002D74; border-color: #002D74; font-weight: 700;">Status</a>
                {% else %}
                <a href="{% url 'telemetry:requests' %}" class="btn-underline" style="text-decoration: none; font-size: 0.9rem; color: #002D74; font-weight: 700;">Requests</a>
                <!-- Mods Dropdown (Hamburger) -->
                <div class="dropdown" style="position: relative; display: inline-block;">
                    <label class="hamburger" onclick="toggleDropdown('modsDropdown', event)" style="margin-left: 10px;">
                        <input type="checkbox" id="hamburger-checkbox" />
                        <svg viewBox="0 0 32 32">
                            <path class="line line-top-bottom" d="M27 10 13 10C10.8 10 9 8.2 9 6 9 3.5 10.8 2 13 2 15.2 2 17 3.8 17 6L17 26C17 28.2 18.8 30 21 30 23.2 30 25 28.2 25 26 25 23.8 23.2 22 21 22L7 22"></path>
                            <path class="line" d="M7 16 27 16"></path>
                        </svg>
                    </label>
                    <div id="modsDropdown" class="dropdown-content" style="display: none; position: absolute; top: 100%; left: 0; background-color: #fff; min-width: 180px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); z-index: 1000; border: 1px solid #002D74; margin-top: 5px;">
                        <a href="#" onclick="selectMod('main', event)" style="color: #002D74; padding: 12px 16px; text-decoration: none; display: block; font-weight: 600; border-bottom: 1px solid #e2e8f0;">Main</a>
                        <div class="dropdown-submenu" style="position: relative;">
                            <a href="#" onclick="toggleDropdown('testingDropdown', event)" style="color: #002D74; padding: 12px 16px; text-decoration: none; display: flex; justify-content: space-between; font-weight: 600; border-bottom: 1px solid #e2e8f0;">Testing Mode <span>▶</span></a>
                            <div id="testingDropdown" class="dropdown-content submenu-content" style="display: none; position: absolute; left: 100%; top: 0; background-color: #fff; min-width: 160px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); border: 1px solid #002D74;">
                                <a href="#" onclick="selectMod('test_phone', event)" style="color: #002D74; padding: 12px 16px; text-decoration: none; display: block; font-weight: 600; border-bottom: 1px solid #e2e8f0;">Phone Mode</a>
                                <a href="#" onclick="selectMod('test_drone', event)" style="color: #002D74; padding: 12px 16px; text-decoration: none; display: block; font-weight: 600;">Drone Mode</a>
                            </div>
                        </div>
                        <a href="#" onclick="selectMod('simulator', event)" style="color: #002D74; padding: 12px 16px; text-decoration: none; display: block; font-weight: 600;">Simulator</a>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <!-- CENTER BRAND -->
            <div class="nav-center" style="display: flex; align-items: center; justify-content: center; flex: 1;">
                <div class="nav-brand" style="display: flex; align-items: center; gap: 0.75rem;">
                    <div class="brand-icon" style="background-color: #002D74; color: white; border-radius: 0; padding: 4px;">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/>
                            <circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>
                        </svg>
                    </div>
                    <div class="brand-text">
                        <div class="brand-title" style="color: #002D74; font-weight: 800; font-size: 1.2rem; line-height: 1;">UTM</div>
                        {% if request.session.user_role == 'PILOT' %}
                        <div class="brand-subtitle" style="color: #002D74; font-size: 0.75rem;">{{ request.session.user_name|default:"Pilot" }}</div>
                        {% else %}
                        <div class="brand-subtitle" style="color: #002D74; font-size: 0.75rem;">Unified Telemetry Monitor</div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- RIGHT CORNER -->
            <div class="nav-right" style="display: flex; align-items: center; justify-content: flex-end; gap: 1rem; flex: 1;">
                {% if request.session.user_role == 'GUEST' or request.user.username == 'guest' %}
                <div style="border: 1px solid #e5e7eb; padding: 0.25rem 0.5rem; display: flex; align-items: center; gap: 0.75rem; background: #fff;">
                    <div style="display: flex; flex-direction: column;">
                        <span style="color: #64748b; font-size: 0.65rem; text-transform: uppercase;">Register your drone</span>
                        <span style="color: #002D74; font-weight: 800; font-size: 1.1rem; line-height: 1;">Drone</span>
                    </div>
                    <a href="{% url 'telemetry:register' %}" style="background-color: #dc2626; color: white; padding: 0.4rem 0.8rem; text-decoration: none; font-weight: 700; font-size: 0.8rem;">REGISTER</a>
                </div>
                {% else %}
                <!-- Phone Status Indicator -->
                <div class="connection-status disconnected" id="connectionStatusPill" style="border-radius: 0;">
                    <span class="status-indicator-dot dot-red" id="statusDot"></span>
                    <span class="status-label" id="statusLabel">?? Phone Disconnected</span>
                </div>
                
                {% if request.session.user_role == 'PILOT' %}
                <a href="{% url 'telemetry:history' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; border-radius: 0; color: #002D74; border-color: #002D74; font-weight: 700;">History</a>
                {% else %}
                <!-- ATC specific Right tools -->
                <button class="btn btn-outline btn-sm" id="btnToggleTester" title="Open ESP32 API Test Panel" style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; color: #002D74; border-color: #002D74; border-radius: 0;">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                    </svg>
                    <span>API Tools</span>
                </button>
                {% endif %}
                
                <a href="{% url 'telemetry:logout' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; font-weight: 700; color: #dc2626; border-color: #dc2626; border-radius: 0;">Log out</a>
                {% endif %}
            </div>
        </div>
    </header>'''

# regex replace
content = re.sub(r'<!-- TOP NAVIGATION BAR -->\s*<header class="navbar" role="banner">.*?</header>', new_header, content, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
