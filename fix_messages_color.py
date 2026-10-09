import re

with open('telemetry/auth_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('messages.info(request, \'Guest has logged out safely.\')', 'messages.success(request, \'You have been logged out safely.\')')
content = content.replace('messages.info(request, \'You have been logged out safely.\')', 'messages.success(request, \'You have been logged out safely.\')')
content = content.replace('messages.info(request, \'Logged in as Guest Observer.\')', 'messages.success(request, \'Logged in as Guest Observer.\')')
content = content.replace('messages.info(request, \'Logged in as Guest Observer with read-only access.\')', 'messages.success(request, \'Logged in as Guest Observer with read-only access.\')')

with open('telemetry/auth_views.py', 'w', encoding='utf-8') as f:
    f.write(content)
