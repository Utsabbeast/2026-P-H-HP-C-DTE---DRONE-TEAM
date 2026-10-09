import re

html_path = 'templates/dashboard.html'
js_path = 'static/js/dashboard.js'

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace the conditional text
old_text = "{% if request.session.user_role == 'ADMIN' or request.session.user_role == 'ATC' %}Main Mode{% else %}User Dashboard{% endif %}"
new_text = "{% if request.session.user_role == 'ADMIN' or request.session.user_role == 'ATC' %}Main Mode{% elif request.session.user_role == 'GUEST' %}Guest Dashboard{% else %}User Dashboard{% endif %}"

html_content = html_content.replace(old_text, new_text)

# Add window.MAIN_MODE_TITLE
script_tag = f"""<script>
    window.MAIN_MODE_TITLE = "{new_text} (Overview)";
</script>
</head>"""

if 'window.MAIN_MODE_TITLE' not in html_content:
    html_content = html_content.replace('</head>', script_tag)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

js_content = js_content.replace(
    "if (elements.mapMainTitle) elements.mapMainTitle.textContent = 'Main Mode (Overview)';",
    "if (elements.mapMainTitle) elements.mapMainTitle.textContent = window.MAIN_MODE_TITLE || 'Main Mode (Overview)';"
)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated dashboard title logic for GUEST.")
