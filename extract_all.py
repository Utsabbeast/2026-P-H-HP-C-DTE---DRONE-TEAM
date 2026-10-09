import os
import re

for filename in os.listdir("templates"):
    if not filename.endswith(".html"): continue
    
    filepath = os.path.join("templates", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False
    
    # Extract CSS
    style_match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if style_match:
        css_content = style_match.group(1).strip()
        css_filename = filename.replace(".html", ".css")
        with open(os.path.join("static", "css", css_filename), "w", encoding="utf-8") as f:
            f.write(css_content)
        html = html[:style_match.start()] + f"<link rel=\"stylesheet\" href=\"{{% static 'css/{css_filename}' %}}\">" + html[style_match.end():]
        changed = True

    # Extract JS
    script_match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    # ignore tailwind script which has src
    script_match2 = re.search(r"<script(?![^>]*src=)[^>]*>(.*?)</script>", html, re.DOTALL)
    if script_match2:
        js_content = script_match2.group(1).strip()
        if js_content:
            js_filename = filename.replace(".html", ".js")
            with open(os.path.join("static", "js", js_filename), "w", encoding="utf-8") as f:
                f.write(js_content)
            html = html[:script_match2.start()] + f"<script src=\"{{% static 'js/{js_filename}' %}}\"></script>" + html[script_match2.end():]
            changed = True

    if changed:
        if "{% load static %}" not in html:
            html = "{% load static %}\n" + html
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Extracted from {filename}")
