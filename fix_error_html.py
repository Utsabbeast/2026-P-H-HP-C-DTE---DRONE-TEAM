import re

files = ['templates/dev_error.html', 'templates/404.html']

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove orphaned </div> after <body>
        content = re.sub(r'(<body[^>]*>)\s*</div>', r'\1', content)

        # Also change bg-gray-50 to bg-white for white background
        content = content.replace('bg-gray-50', 'bg-white')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed orphaned </div> and set bg-white in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
