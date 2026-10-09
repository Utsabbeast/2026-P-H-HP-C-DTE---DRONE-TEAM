import re

filepath = 'templates/status.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's replace the alert with dev-error redirect
content = content.replace("onsubmit=\"event.preventDefault(); alert('This website is under development. We will be making that overall coding part later.');\"", "onsubmit=\"event.preventDefault(); window.location.href='{% url 'telemetry:dev-error' %}';\"")

# Now let's restructure the sequential forms section.
# I will use a regex or string replacement to completely replace the logic from `{% if not pilot_profile %}` down to `{% elif not drone_registration %}`.

old_logic = """        {% if not pilot_profile %}
            <div class="requests-header">
                <h1 class="requests-title">1. Complete Pilot Profile</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem;">
                <form onsubmit="event.preventDefault(); window.location.href='{% url 'telemetry:dev-error' %}';" method="POST" action="{% url 'telemetry:status' %}" style="display: flex; flex-direction: column; gap: 1rem;">
                    {% csrf_token %}
                    <input type="hidden" name="form_type" value="profile">
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Pilot License Number</label>
                        <input type="text" name="license" placeholder="Optional" style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <button type="submit" style="background: #002D74; color: white; padding: 1rem; border: none; font-weight: 600; cursor: pointer;">Submit Profile for Approval</button>
                </form>
            </div>
        {% elif pilot_profile.status != 'APPROVED' %}
            <div class="requests-header">
                <h1 class="requests-title">Profile Pending</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem; text-align: center; border-color: #d97706; background: #fff8f1;">
                <p style="color: #d97706; font-weight: 600; font-size: 1.1rem;">Your Pilot Profile is currently under review by ATC Admin.</p>
                <p style="color: #666; margin-top: 0.5rem;">Please wait for approval before registering a drone.</p>
            </div>
        {% elif not drone_registration %}"""

new_logic = """        {% if not pilot_profile or pilot_profile.status != 'APPROVED' %}
            
            {% if not pilot_profile %}
                <div class="requests-header">
                    <h1 class="requests-title">1. Complete Pilot Profile</h1>
                </div>
                <div class="requests-table-container" style="padding: 2rem;">
                    <form onsubmit="event.preventDefault(); window.location.href='{% url 'telemetry:dev-error' %}';" method="POST" action="{% url 'telemetry:status' %}" style="display: flex; flex-direction: column; gap: 1rem;">
                        {% csrf_token %}
                        <input type="hidden" name="form_type" value="profile">
                        <div>
                            <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Pilot License Number</label>
                            <input type="text" name="license" placeholder="Optional" style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                        </div>
                        <button type="submit" style="background: #002D74; color: white; padding: 1rem; border: none; font-weight: 600; cursor: pointer;">Submit Profile for Approval</button>
                    </form>
                </div>
            {% else %}
                <div class="requests-header">
                    <h1 class="requests-title">Profile Pending</h1>
                </div>
                <div class="requests-table-container" style="padding: 2rem; text-align: center; border-color: #d97706; background: #fff8f1;">
                    <p style="color: #d97706; font-weight: 600; font-size: 1.1rem;">Your Pilot Profile is currently under review by ATC Admin.</p>
                    <p style="color: #666; margin-top: 0.5rem;">Please wait for approval before registering a drone.</p>
                </div>
            {% endif %}

            <!-- ALWAYS show drone registration but disabled -->
            <div class="requests-header">
                <h1 class="requests-title">2. Drone Registration</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem; opacity: 0.6; pointer-events: none;">
                <form onsubmit="event.preventDefault(); window.location.href='{% url 'telemetry:dev-error' %}';" method="POST" action="{% url 'telemetry:status' %}" style="display: flex; flex-direction: column; gap: 1rem;">
                    {% csrf_token %}
                    <input type="hidden" name="form_type" value="drone">
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem; color: #94a3b8;">Drone Model / Name</label>
                        <input type="text" name="drone_name" disabled style="width: 100%; padding: 0.8rem; border: 1px solid #e2e8f0; font-family: inherit; background: #f8fafc; color: #94a3b8;">
                    </div>
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem; color: #94a3b8;">UIN (Unique ID)</label>
                        <input type="text" name="uin" disabled style="width: 100%; padding: 0.8rem; border: 1px solid #e2e8f0; font-family: inherit; background: #f8fafc; color: #94a3b8;">
                    </div>
                    <button type="submit" disabled style="background: #94a3b8; color: white; padding: 1rem; border: none; font-weight: 600; cursor: not-allowed;">Submit Drone Registration</button>
                </form>
            </div>
            
        {% elif not drone_registration %}"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced logic successfully.")
else:
    print("Could not find the target string. The first replacement might have altered it.")
