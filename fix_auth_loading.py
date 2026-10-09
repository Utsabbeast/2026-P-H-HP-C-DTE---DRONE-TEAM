import re

with open('telemetry/auth_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('telemetry:loading', 'telemetry:dashboard')
content = re.sub(r'class UTMLoadingView\(View\):.*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)

with open('telemetry/auth_views.py', 'w', encoding='utf-8') as f:
    f.write(content)
