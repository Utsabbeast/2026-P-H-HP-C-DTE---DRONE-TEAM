import re

filepath = 'templates/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the line with "Review Dashboard" spanning until </button>
content = re.sub(r'<button onclick="window\.open.*?<span>Review Dashboard</span></button>', '', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed old button.")
