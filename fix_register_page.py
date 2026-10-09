import re

filepath = 'templates/register.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Title
content = content.replace('Drone Registration', 'Profile Registration')

# Fix Image
content = content.replace("src=\"{% static 'img/drone2.jpg' %}\"", "src=\"{% static 'img/Image 1.jpeg' %}\"")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed register.html")
