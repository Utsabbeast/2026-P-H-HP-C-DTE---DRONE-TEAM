file_path = 'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/static/js/login.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("window.location.href = '/quick-login/guest/';", "window.location.replace('/quick-login/guest/');")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
