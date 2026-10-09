import os

filepath = 'templates/status.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '<form method="POST" action="{% url \'telemetry:status\' %}"'
replacement = '<form onsubmit="event.preventDefault(); alert(\'This website is under development. We will be making that overall coding part later.\');" method="POST" action="{% url \'telemetry:status\' %}"'

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated forms in status.html')
else:
    print('Target string not found')
