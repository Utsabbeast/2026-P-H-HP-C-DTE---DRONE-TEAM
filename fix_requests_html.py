import sys

content = open('templates/requests.html', 'r', encoding='utf-8').read()

new_table = """        <div class="requests-header" style="margin-top: 3rem;">
            <h2 class="requests-title">Profile Acceptance</h2>
        </div>

        <div class="requests-table-container">
            <table class="requests-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>User</th>
                        <th>License Number</th>
                        <th>Status</th>
                        <th>Date</th>
                        {% if is_atc %}
                        <th>Actions</th>
                        {% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for profile in profile_requests %}
                    <tr>
                        <td style="font-family: var(--font-mono);">#{{ profile.id }}</td>
                        <td style="font-weight: 600;">{{ profile.user.username }}</td>
                        <td>{{ profile.license_number|default:"N/A" }}</td>
                        <td><span class="status-badge status-{{ profile.status }}">{{ profile.get_status_display }}</span></td>
                        <td style="font-size: 0.85rem; color: var(--text-secondary);">{{ profile.created_at|date:"M d, H:i" }}</td>
                        {% if is_atc %}
                        <td>
                            {% if profile.status == 'PENDING' %}
                            <div class="action-buttons">
                                <button class="btn-outline" onclick="alert('Profile Approved (Simulated)')">Approve</button>
                                <button class="btn-primary" onclick="alert('Profile Rejected (Simulated)')">Reject</button>
                            </div>
                            {% else %}
                            <span style="font-size: 0.75rem; color: var(--text-secondary);">Processed</span>
                            {% endif %}
                        </td>
                        {% endif %}
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="{% if is_atc %}6{% else %}5{% endif %}" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                            No profile acceptance requests found.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="requests-header" style="margin-top: 3rem;">
            <h2 class="requests-title">Drone Registrations (UIN)</h2>"""

if 'Profile Acceptance' not in content:
    content = content.replace('<div class="requests-header" style="margin-top: 3rem;">\n            <h2 class="requests-title">Drone Registrations (UIN)</h2>', new_table)

open('templates/requests.html', 'w', encoding='utf-8').write(content)
print("Updated requests.html")
