import re

filepath = 'urls.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = "path('dev-error/', views.DevErrorView.as_view(), name='dev-error'),"
replacement = "path('dev-error/', views.DevErrorView.as_view(), name='dev-error'),\n    path('user-database/', views.UserDatabaseView.as_view(), name='user-database'),"

if pattern in content:
    content = content.replace(pattern, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added user-database URL to urls.py")
else:
    print("Could not find pattern in urls.py")
