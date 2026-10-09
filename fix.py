with open("templates/login.html", "r", encoding="utf-8") as f:
    content = f.read()

content = "{% load static %}\n" + content
content = content.replace("url('left%20side.jpg')", "url('{% static \"img/left side.jpg\" %}')")
content = content.replace("url('login%20img.png')", "url('{% static \"img/login img.png\" %}')")
content = content.replace('"Logo1.svg"', '"{% static \'img/Logo1.svg\' %}"')
content = content.replace('"Logo2.jpg"', '"{% static \'img/Logo2.jpg\' %}"')
content = content.replace('"Logo3.png"', '"{% static \'img/Logo3.png\' %}"')
content = content.replace('"login img.png"', '"{% static \'img/login img.png\' %}"')
content = content.replace('"login%20img.png"', '"{% static \'img/login img.png\' %}"')
content = content.replace('"left side.jpg"', '"{% static \'img/left side.jpg\' %}"')

with open("templates/login.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
