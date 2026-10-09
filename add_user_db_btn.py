import re

filepath = 'templates/requests.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = """        <div class="requests-header" style="margin-top: 2rem;">
            <h2 class="requests-title">Flight Permission Requests</h2>
        </div>"""

replacement = """        <div class="requests-header" style="margin-top: 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #002D74; padding-bottom: 0.5rem; margin-bottom: 1.5rem;">
            <h2 class="requests-title" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0;">Flight Permission Requests</h2>
            {% if request.session.user_role == 'ADMIN' %}
            <a href="{% url 'telemetry:user-database' %}" style="background: #002D74; color: white; padding: 0.6rem 1.2rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; text-decoration: none; transition: background 0.3s;">
                User Database
            </a>
            {% endif %}
        </div>"""

if pattern in content:
    content = content.replace(pattern, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated requests.html with User Database button")
else:
    print("Could not find pattern in requests.html")
