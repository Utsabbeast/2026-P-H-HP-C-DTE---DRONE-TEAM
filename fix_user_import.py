import sys

content = open('telemetry/models.py', 'r', encoding='utf-8').read()

if 'from django.contrib.auth.models import User' in content:
    content = content.replace('from django.contrib.auth.models import User', '')
    
content = 'from django.contrib.auth.models import User\n' + content

open('telemetry/models.py', 'w', encoding='utf-8').write(content)

print("Fixed User import in models.py")
