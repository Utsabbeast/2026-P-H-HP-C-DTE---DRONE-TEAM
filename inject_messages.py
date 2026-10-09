import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add messages.html before </body>
if '{% include \'messages.html\' %}' not in content:
    content = content.replace('</body>', '{% include \'messages.html\' %}\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
