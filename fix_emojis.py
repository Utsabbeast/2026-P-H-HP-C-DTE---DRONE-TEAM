import re

with open('telemetry/auth_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emojis
content = content.replace('✅ ', '')
content = content.replace('⚡ ', '')
content = content.replace('✈️ ', '')
content = content.replace('👁️ ', '')
content = content.replace('⚠️ ', '')
content = content.replace('❌ ', '')

with open('telemetry/auth_views.py', 'w', encoding='utf-8') as f:
    f.write(content)
