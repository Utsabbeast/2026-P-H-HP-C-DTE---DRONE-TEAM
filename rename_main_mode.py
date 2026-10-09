import re

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the dropdown text
content = content.replace(
    'border-bottom: 1px solid #e2e8f0;">Main Mode</a>',
    'border-bottom: 1px solid #e2e8f0;">{% if request.session.user_role == \'ADMIN\' or request.session.user_role == \'ATC\' %}Main Mode{% else %}User Dashboard{% endif %}</a>'
)

# Replace the JS title
content = content.replace(
    'mapTitle.innerText = "Main Mode";',
    'mapTitle.innerText = "{% if request.session.user_role == \'ADMIN\' or request.session.user_role == \'ATC\' %}Main Mode{% else %}User Dashboard{% endif %}";'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Main Mode renamed for user.")
