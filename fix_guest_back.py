import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change guest back button to point to logout
content = content.replace('href="{% url \'telemetry:login\' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; font-weight: 700; color: #002D74; border-color: #002D74; border-radius: 0;">&larr; Back</a>',
                          'href="{% url \'telemetry:logout\' %}" class="btn-outline" style="padding: 0.5rem 1rem; text-decoration: none; font-weight: 700; color: #002D74; border-color: #002D74; border-radius: 0;">&larr; Back</a>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
