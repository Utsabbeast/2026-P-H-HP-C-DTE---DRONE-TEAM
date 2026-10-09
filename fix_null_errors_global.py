import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: elements.someProp.style... = ...
content = re.sub(r'(\s+)elements\.([a-zA-Z0-9_]+)\.style\.(display|background|color|borderColor)\s*=', r'\1if (elements.\2) elements.\2.style.\3 =', content)

# Pattern: elements.someProp.textContent = ...
content = re.sub(r'(\s+)elements\.([a-zA-Z0-9_]+)\.textContent\s*=', r'\1if (elements.\2) elements.\2.textContent =', content)

# Fix duplicate ifs
content = re.sub(r'if \(elements\.([a-zA-Z0-9_]+)\)\s*if \(elements\.\1\)', r'if (elements.\1)', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated null checks globally for elements.*")
