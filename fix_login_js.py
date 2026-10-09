import sys

content = open('static/js/login.js', 'r', encoding='utf-8').read()

old_showRoles = """        function showRoles() {
            document.getElementById('role-selection').classList.remove('hidden');
            document.getElementById('login-form-view').classList.add('hidden');
            // reset fields
            document.querySelector('form').reset();
            password.setAttribute('type', 'password');
            togglePassword.classList.remove('hidden');
            eyeSlash.classList.add('hidden');
        }"""

new_showRoles = """        function showRoles() {
            document.getElementById('role-selection').classList.remove('hidden');
            document.getElementById('login-form-view').classList.add('hidden');
            // reset fields
            document.querySelector('form').reset();
            password.setAttribute('type', 'password');
            togglePassword.classList.remove('hidden');
            eyeSlash.classList.add('hidden');
            let msgBox = document.getElementById('inline-msg-box');
            if (msgBox) {
                msgBox.classList.add('hidden');
            }
        }"""

content = content.replace(old_showRoles, new_showRoles)
open('static/js/login.js', 'w', encoding='utf-8').write(content)
print("Updated login.js with message box reset")
