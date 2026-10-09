import sys

content = open('static/js/login.js', 'r', encoding='utf-8').read()

# Add DOMContentLoaded listener to reset the view
reset_code = """
        // Ensure the page resets to Role Selection on refresh
        document.addEventListener('DOMContentLoaded', function() {
            showRoles();
        });
"""

if "DOMContentLoaded" not in content:
    content += reset_code

open('static/js/login.js', 'w', encoding='utf-8').write(content)
print("Updated login.js with DOMContentLoaded reset")
