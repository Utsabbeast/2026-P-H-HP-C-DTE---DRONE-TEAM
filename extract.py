import os
import re

with open("templates/login.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract CSS
style_match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
if style_match:
    css_content = style_match.group(1).strip()
    with open("static/css/login.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    html = html[:style_match.start()] + "<link rel=\"stylesheet\" href=\"{% static 'css/login.css' %}\">" + html[style_match.end():]

# Extract JS
script_match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
if script_match:
    js_content = script_match.group(1).strip()
    with open("static/js/login.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    html = html[:script_match.start()] + "<script src=\"{% static 'js/login.js' %}\"></script>" + html[script_match.end():]

with open("templates/login.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Extracted CSS and JS.")
