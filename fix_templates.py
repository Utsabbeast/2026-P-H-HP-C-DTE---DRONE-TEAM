import sys
import os

# Fix status.html
content = open('templates/status.html', 'r', encoding='utf-8').read()
content = content.replace('.requests-table-container { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 0; overflow-x: auto; margin-bottom: 3rem; }', 
'.requests-container { display: flex; flex-direction: column; align-items: center; }\n    .requests-table-container { background: #f0f7ff; border: 2px solid #002D74; box-shadow: 0 8px 16px -4px rgba(0,45,116,0.15); border-radius: 8px; overflow-x: auto; margin-bottom: 3rem; width: 100%; max-width: 800px; padding: 2rem; }')
content = content.replace('<form onsubmit="event.preventDefault(); submitRequest();"', '<form method="POST" action="{% url \'telemetry:status\' %}"')
content = content.replace('max-width: 600px;">', 'max-width: 100%;">\n                {% csrf_token %}')
content = content.replace('id="locName"', 'name="locName" id="locName"')
content = content.replace('id="locLat"', 'name="locLat" id="locLat"')
content = content.replace('id="locLon"', 'name="locLon" id="locLon"')
content = content.replace('id="maxAlt"', 'name="maxAlt" id="maxAlt"')
content = content.replace('id="purpose"', 'name="purpose" id="purpose"')
content = content.replace('<script src="{% static \'js/status_inline.js\' %}"></script>', '')
open('templates/status.html', 'w', encoding='utf-8').write(content)

# Fix history.html
content2 = open('templates/history.html', 'r', encoding='utf-8').read()
content2 = content2.replace('.history-table-container { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 0; overflow-x: auto; margin-bottom: 3rem; }',
'.requests-container { display: flex; flex-direction: column; align-items: center; }\n    .history-table-container { background: #f0f7ff; border: 2px solid #002D74; box-shadow: 0 8px 16px -4px rgba(0,45,116,0.15); border-radius: 8px; overflow-x: auto; margin-bottom: 3rem; width: 100%; max-width: 1000px; padding: 1rem; }')
content2 = content2.replace('class="requests-table-container"', 'class="history-table-container"')
open('templates/history.html', 'w', encoding='utf-8').write(content2)

print("Done updating templates")
