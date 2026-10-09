import sys

content = open('templates/status.html', 'r', encoding='utf-8').read()

old_form_section = """        <!-- Request Form Section -->
        <div class="requests-header">
            <h1 class="requests-title">Submit New Flight Request</h1>
        </div>
        <div class="requests-table-container" style="padding: 2rem;">
            <form method="POST" action="{% url 'telemetry:status' %}"
                style="display: flex; flex-direction: column; gap: 1rem; max-width: 100%;">
                {% csrf_token %}
                <div>
                    <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Location Name</label>
                    <input type="text" name="locName" id="locName" placeholder="e.g. Ludhiana Sector 4" required
                        style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                </div>
                <div style="display: flex; gap: 1rem;">
                    <div style="flex: 1;">
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Latitude</label>
                        <input type="number" step="any" name="locLat" id="locLat" required value="30.900965"
                            style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <div style="flex: 1;">
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Longitude</label>
                        <input type="number" step="any" name="locLon" id="locLon" required value="75.857275"
                            style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                </div>
                <div>
                    <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Max Altitude (m)</label>
                    <input type="number" name="maxAlt" id="maxAlt" required value="120"
                        style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                </div>
                <div>
                    <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Purpose</label>
                    <textarea name="purpose" id="purpose" required
                        style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit; height: 100px;"></textarea>
                </div>
                <button type="submit"
                    style="background: #002D74; color: white; padding: 1rem; border: none; font-weight: 600; cursor: pointer; margin-top: 1rem;">Submit
                    Request for ATC Approval</button>
            </form>
        </div>"""

new_form_section = """        <!-- Sequential Forms Section -->
        {% if not pilot_profile %}
            <div class="requests-header">
                <h1 class="requests-title">1. Complete Pilot Profile</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem;">
                <form method="POST" action="{% url 'telemetry:status' %}" style="display: flex; flex-direction: column; gap: 1rem;">
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
        {% elif not drone_registration %}
            <div class="requests-header">
                <h1 class="requests-title">2. Drone Registration</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem;">
                <form method="POST" action="{% url 'telemetry:status' %}" style="display: flex; flex-direction: column; gap: 1rem;">
                    {% csrf_token %}
                    <input type="hidden" name="form_type" value="drone">
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Drone Model / Name</label>
                        <input type="text" name="drone_name" required style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">UIN (Unique ID)</label>
                        <input type="text" name="uin" required style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <button type="submit" style="background: #002D74; color: white; padding: 1rem; border: none; font-weight: 600; cursor: pointer;">Submit Drone Registration</button>
                </form>
            </div>
        {% elif drone_registration.status != 'APPROVED' %}
            <div class="requests-header">
                <h1 class="requests-title">Drone Registration Pending</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem; text-align: center; border-color: #d97706; background: #fff8f1;">
                <p style="color: #d97706; font-weight: 600; font-size: 1.1rem;">Your Drone Registration is currently under review by ATC Admin.</p>
                <p style="color: #666; margin-top: 0.5rem;">Please wait for approval before submitting flight requests.</p>
            </div>
        {% else %}
            
            <div class="requests-header">
                <h1 class="requests-title">Current Flight Permission Status</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem; margin-bottom: 2rem;">
                {% if flight_requests %}
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <tr style="border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 0.5rem;">Location</th>
                            <th style="padding: 0.5rem;">Max Alt.</th>
                            <th style="padding: 0.5rem;">Status</th>
                            <th style="padding: 0.5rem;">Date</th>
                        </tr>
                        {% for req in flight_requests %}
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 0.8rem 0.5rem;">{{ req.location_name }}</td>
                            <td style="padding: 0.8rem 0.5rem;">{{ req.max_altitude }}m</td>
                            <td style="padding: 0.8rem 0.5rem;">
                                {% if req.status == 'PENDING' %} <span style="color: #d97706; font-weight:bold;">Pending</span>
                                {% elif req.status == 'APPROVED' %} <span style="color: #15803d; font-weight:bold;">Approved</span>
                                {% else %} <span style="color: #b91c1c; font-weight:bold;">Rejected</span> {% endif %}
                            </td>
                            <td style="padding: 0.8rem 0.5rem; font-size: 0.9rem; color: #666;">{{ req.created_at|date:"M d, Y" }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                {% else %}
                    <p style="text-align: center; color: #666;">No flight permission requests submitted yet.</p>
                {% endif %}
            </div>

            <div class="requests-header">
                <h1 class="requests-title">3. Submit Flight Permission Request</h1>
            </div>
            <div class="requests-table-container" style="padding: 2rem;">
                <form method="POST" action="{% url 'telemetry:status' %}"
                    style="display: flex; flex-direction: column; gap: 1rem; max-width: 100%;">
                    {% csrf_token %}
                    <input type="hidden" name="form_type" value="flight">
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Location Name</label>
                        <input type="text" name="locName" id="locName" placeholder="e.g. Ludhiana Sector 4" required
                            style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <div style="flex: 1;">
                            <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Latitude</label>
                            <input type="number" step="any" name="locLat" id="locLat" required value="30.900965"
                                style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                        </div>
                        <div style="flex: 1;">
                            <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Longitude</label>
                            <input type="number" step="any" name="locLon" id="locLon" required value="75.857275"
                                style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                        </div>
                    </div>
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Max Altitude (m)</label>
                        <input type="number" name="maxAlt" id="maxAlt" required value="120"
                            style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit;">
                    </div>
                    <div>
                        <label style="font-weight: 600; display: block; margin-bottom: 0.5rem;">Purpose</label>
                        <textarea name="purpose" id="purpose" required
                            style="width: 100%; padding: 0.8rem; border: 1px solid var(--border-color); font-family: inherit; height: 100px;"></textarea>
                    </div>
                    <button type="submit"
                        style="background: #002D74; color: white; padding: 1rem; border: none; font-weight: 600; cursor: pointer; margin-top: 1rem;">Submit
                        Request for ATC Approval</button>
                </form>
            </div>
        {% endif %}"""

content = content.replace(old_form_section, new_form_section)

open('templates/status.html', 'w', encoding='utf-8').write(content)
print("Updated status.html")
