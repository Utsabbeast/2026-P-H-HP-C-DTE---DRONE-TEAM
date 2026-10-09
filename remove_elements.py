import re

files = ['templates/dev_error.html', 'templates/404.html']

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove Top Bar
        content = re.sub(r'<!-- Top Bar -->\s*<div class="absolute top-0 left-0 w-full h-8 z-50">.*?</div>\s*</div>', '', content, flags=re.DOTALL)
        
        # Remove Footer Copyright
        content = re.sub(r'<!-- Footer Copyright -->\s*<a href="[^"]+" class="absolute bottom-4 right-6[^>]+>.*?</a>', '', content, flags=re.DOTALL)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Removed Top Bar and Footer from {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
