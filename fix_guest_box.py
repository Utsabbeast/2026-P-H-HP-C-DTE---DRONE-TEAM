import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Guest Register box in the nav-right
old_box = '''                {% if request.session.user_role == 'GUEST' or request.user.username == 'guest' %}
                <div style="border: 1px solid #e5e7eb; padding: 0.25rem 0.5rem; display: flex; align-items: center; gap: 0.75rem; background: #fff;">
                    <div style="display: flex; flex-direction: column;">
                        <span style="color: #64748b; font-size: 0.65rem; text-transform: uppercase;">Register your drone</span>
                        <span style="color: #002D74; font-weight: 800; font-size: 1.1rem; line-height: 1;">Drone</span>
                    </div>
                    <a href="{% url 'telemetry:register' %}" style="background-color: #dc2626; color: white; padding: 0.4rem 0.8rem; text-decoration: none; font-weight: 700; font-size: 0.8rem;">REGISTER</a>
                </div>'''

new_box = '''                {% if request.session.user_role == 'GUEST' or request.user.username == 'guest' %}
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #002D74; font-size: 0.8rem; font-weight: 600;">Drone</span>
                    <a href="{% url 'telemetry:register' %}" style="color: #dc2626; text-decoration: none; font-weight: 700; font-size: 0.8rem;">Register</a>
                </div>'''

content = content.replace(old_box, new_box)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
