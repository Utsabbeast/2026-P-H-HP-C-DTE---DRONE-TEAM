import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

bad_string = "const isHidden = if (elements.testerPanel) elements.testerPanel.style.display === 'none';"
good_string = "const isHidden = elements.testerPanel && elements.testerPanel.style.display === 'none';"

if bad_string in content:
    content = content.replace(bad_string, good_string)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed syntax error in dashboard.js")
else:
    print("Could not find bad string")
