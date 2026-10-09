import re

filepath = 'templates/dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the inline onclick handler from btnToggleTester
pattern = r' onclick="event\.stopPropagation\(\); const tp = document\.getElementById\(\'testerPanel\'\); if\(tp\)\{ const isHidden = tp\.style\.display === \'none\'; tp\.style\.display = isHidden \? \'block\' : \'none\'; if\(isHidden\) tp\.scrollIntoView\(\{behavior: \'smooth\'\}\); \}"'
content = re.sub(pattern, '', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed inline onclick from API Tools button")
