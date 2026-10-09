import os

filepath = 'templates/register.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''<div style="text-align: center; margin: 40px 0;">
    <h2 style="font-weight: 800; color: #002D74; font-size: 2rem;">COMING SOON</h2>
    <p style="color: #64748b; margin-top: 10px;">Registration is currently unavailable.</p>
</div>'''

replacement = '''<form method="POST" action="{% url 'telemetry:register' %}" class="flex flex-col gap-4 mt-8">
                    {% csrf_token %}
                    <input class="p-3 border border-gray-300 bg-white text-[#002D74] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400 shadow-sm transition-all font-medium" type="text" name="username" placeholder="Username" required>
                    <input class="p-3 border border-gray-300 bg-white text-[#002D74] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400 shadow-sm transition-all font-medium" type="email" name="email" placeholder="Email Address" required>
                    <input class="p-3 border border-gray-300 w-full bg-white text-[#002D74] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400 shadow-sm transition-all font-medium" type="password" name="password" placeholder="Password" required>
                    <input class="p-3 border border-gray-300 w-full bg-white text-[#002D74] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-400 shadow-sm transition-all font-medium" type="password" name="confirm_password" placeholder="Confirm Password" required>
                    <button class="btn-96 btn-navy shadow-lg border border-gray-300 mt-2" type="submit"><span>Create Account</span></button>
                </form>'''

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated register.html form')
else:
    print('Target string not found in register.html')
