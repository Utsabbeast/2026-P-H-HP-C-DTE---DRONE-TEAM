import os

filepath = 'templates/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''<a href="#" onclick="document.getElementById('inline-msg-box').textContent = 'Coming soon...'; document.getElementById('inline-msg-box').classList.remove('hidden'); return false;" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>'''
replacement = '''<a href="{% url 'telemetry:register' %}" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>'''

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated login.html register button link')
else:
    print('Target string not found in login.html')
