import re

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure it's display: none initially in html
old_style = 'style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; color: #002D74; border-color: #002D74; border-radius: 0;"'
new_style = 'style="display: none; align-items: center; gap: 6px; padding: 6px 12px; color: #002D74; border-color: #002D74; border-radius: 0;"'

if old_style in content:
    content = content.replace(old_style, new_style)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dashboard.html API button initial display to none")
