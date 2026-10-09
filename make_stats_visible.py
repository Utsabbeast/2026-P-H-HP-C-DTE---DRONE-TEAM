import re

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Change max-width to allow full text, and opacity to 1
content = content.replace(
    'max-width: 40px;',
    'max-width: 250px;'
)
content = content.replace(
    'opacity: 0;',
    'opacity: 1;'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Overall stats now fully visible.")
