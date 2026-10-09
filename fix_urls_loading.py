import re

with open('telemetry/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'path\(\'loading/\',.*?name=\'loading\'\),', '', content)

with open('telemetry/urls.py', 'w', encoding='utf-8') as f:
    f.write(content)
