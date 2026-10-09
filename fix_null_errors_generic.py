import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace assignments in updateConnectionStatus generically
start_idx = content.find('function updateConnectionStatus')
end_idx = content.find('// Polling Logic', start_idx)

original_func = content[start_idx:end_idx]

# Pattern: elements.someProp.className = ...
# Replace with: if (elements.someProp) elements.someProp.className = ...
new_func = re.sub(r'(\s+)elements\.([a-zA-Z0-9_]+)\.className\s*=', r'\1if (elements.\2) elements.\2.className =', original_func)

# Pattern: elements.someProp.textContent = ...
new_func = re.sub(r'(\s+)elements\.([a-zA-Z0-9_]+)\.textContent\s*=', r'\1if (elements.\2) elements.\2.textContent =', new_func)

# Pattern: elements.someProp.style.color = ...
new_func = re.sub(r'(\s+)elements\.([a-zA-Z0-9_]+)\.style\.color\s*=', r'\1if (elements.\2) elements.\2.style.color =', new_func)

# Fix duplicate ifs if they already have an if:
# e.g. "if (elements.statusHeartbeatSec) if (elements.statusHeartbeatSec) ..."
new_func = re.sub(r'if \(elements\.([a-zA-Z0-9_]+)\)\s*if \(elements\.\1\)', r'if (elements.\1)', new_func)

# Update Banner classes
# if (elements.hotspotBanner) elements.hotspotBanner.classList.add('is-connected'); -> already has if

content = content[:start_idx] + new_func + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated generically")
