import re

filepath = 'templates/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the page loader div
loader_div_pattern = r'<!-- Full Page Loader -->\s*<div id="page-loader".*?</div>\s*</div>\s*</div>'
# The page-loader div might be nested, let's use a non-greedy regex or just simple string replacement
# Let's inspect the loader div first.
