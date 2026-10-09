import re

with open('templates/register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace everything inside the <form> to just say COMING SOON
new_form = '''
<div style="text-align: center; margin: 40px 0;">
    <h2 style="font-weight: 800; color: #002D74; font-size: 2rem;">COMING SOON</h2>
    <p style="color: #64748b; margin-top: 10px;">Registration is currently unavailable.</p>
</div>
'''

content = re.sub(r'<form.*?</form>', new_form, content, flags=re.DOTALL)

with open('templates/register.html', 'w', encoding='utf-8') as f:
    f.write(content)
