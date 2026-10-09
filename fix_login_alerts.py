import sys

content = open('templates/login.html', 'r', encoding='utf-8').read()

old_form_top = """                    <div class="flex items-center gap-3">
                        <img src="{% static 'img/login img.png' %}" alt="Login Icon" class="w-8 h-8 object-contain">
                        <h2 id="login-title" class="font-bold text-3xl text-[#002D74] tracking-tight">Login</h2>
                    </div>
                    <p class="text-sm mt-4 text-[#002D74]/80 font-medium">If you are already a member, easily log in now.</p>

                    <form method="POST" action="/login/" class="flex flex-col gap-4">"""

new_form_top = """                    <div class="flex items-center gap-3">
                        <img src="{% static 'img/login img.png' %}" alt="Login Icon" class="w-8 h-8 object-contain">
                        <h2 id="login-title" class="font-bold text-3xl text-[#002D74] tracking-tight">Login</h2>
                    </div>
                    <p class="text-sm mt-4 text-[#002D74]/80 font-medium">If you are already a member, easily log in now.</p>
                    
                    <div id="inline-msg-box" class="hidden mt-4 p-3 bg-red-50 text-red-600 text-sm font-semibold border-l-4 border-red-500 shadow-sm transition-all"></div>

                    <form method="POST" action="/login/" class="flex flex-col gap-4">"""
content = content.replace(old_form_top, new_form_top)

old_buttons = """                    <div onclick="alert('Coming soon')" class="mt-5 text-sm border-b border-[#002D74]/20 py-3 tooltip cursor-pointer hover:text-[#206ab1] text-[#002D74] transition-colors font-semibold">Forget password?</div>

                    <div id="register-section" class="mt-4 text-sm flex justify-between items-center container-mr">
                        <p class="mr-3 md:mr-0 text-[#002D74]/90 font-medium">If you don't have an account..</p>
                        <a href="#" onclick="alert('Contact Admin for now'); return false;" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>
                    </div>"""

# Wait, in the file the code is:
#                     <div onclick="alert('Coming soon')" class="mt-5 text-sm border-b border-[#002D74]/20 py-3 tooltip cursor-pointer hover:text-white text-[#002D74] transition-colors font-semibold">Forget password?</div>
#
#                     <div id="register-section" class="mt-4 text-sm flex justify-between items-center container-mr">
#                         <p class="mr-3 md:mr-0 text-[#002D74]/90 font-medium">If you don't have an account..</p>
#                         <a href="#" onclick="alert('Contact Admin for now'); return false;" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>
#                     </div>

old_buttons_actual = """                    <div onclick="alert('Coming soon')" class="mt-5 text-sm border-b border-[#002D74]/20 py-3 tooltip cursor-pointer hover:text-white text-[#002D74] transition-colors font-semibold">Forget password?</div>

                    <div id="register-section" class="mt-4 text-sm flex justify-between items-center container-mr">
                        <p class="mr-3 md:mr-0 text-[#002D74]/90 font-medium">If you don't have an account..</p>
                        <a href="#" onclick="alert('Contact Admin for now'); return false;" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>
                    </div>"""

new_buttons_actual = """                    <div onclick="document.getElementById('inline-msg-box').textContent = 'Contact Admin'; document.getElementById('inline-msg-box').classList.remove('hidden');" class="mt-5 text-sm border-b border-[#002D74]/20 py-3 tooltip cursor-pointer hover:text-[#206ab1] text-[#002D74] transition-colors font-semibold">Forget password?</div>

                    <div id="register-section" class="mt-4 text-sm flex justify-between items-center container-mr">
                        <p class="mr-3 md:mr-0 text-[#002D74]/90 font-medium">If you don't have an account..</p>
                        <a href="#" onclick="document.getElementById('inline-msg-box').textContent = 'Coming soon...'; document.getElementById('inline-msg-box').classList.remove('hidden'); return false;" class="register text-[#002D74] bg-white border border-gray-300 shadow-sm hover:shadow-md py-2 px-5 hover:bg-gray-50 font-bold duration-300 inline-block text-center text-sm" style="text-decoration:none;">Register</a>
                    </div>"""

content = content.replace(old_buttons_actual, new_buttons_actual)

open('templates/login.html', 'w', encoding='utf-8').write(content)
print("Updated login.html inline messages")
