const togglePassword = document.querySelector('#togglePassword');
        const password = document.querySelector('#password');
        const eyeSlash = document.querySelector('#mama');

        togglePassword.addEventListener('click', function (e) {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('hidden');
            eyeSlash.classList.toggle('hidden');
        });

        eyeSlash.addEventListener('click', function (e) {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('hidden');
            togglePassword.classList.toggle('hidden');
        });

        // Toggle Login Views
        function showLogin(role) {
            document.getElementById('role-selection').classList.add('hidden');
            document.getElementById('login-form-view').classList.remove('hidden');
            document.getElementById('login-title').innerText = role + ' Login';
            
            // Set a hidden field for login_type
            let form = document.querySelector('form');
            let loginTypeInput = form.querySelector('input[name="login_type"]');
            if (!loginTypeInput) {
                loginTypeInput = document.createElement('input');
                loginTypeInput.type = 'hidden';
                loginTypeInput.name = 'login_type';
                form.appendChild(loginTypeInput);
            }
            // Map "Admin" to "atc" and "User" to "pilot"
            loginTypeInput.value = (role === 'Admin') ? 'atc' : 'pilot';
            
            if(role === 'User') {
                document.getElementById('register-section').classList.remove('hidden');
                document.getElementById('register-section').classList.add('flex');
            } else {
                document.getElementById('register-section').classList.remove('flex');
                document.getElementById('register-section').classList.add('hidden');
            }
        }

        function showRoles() {
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
        }

        function guestLogin() {
            window.location.href = '/quick-login/guest/';
        }
        // Ensure the page resets to Role Selection on refresh
        document.addEventListener('DOMContentLoaded', function() {
            showRoles();
        });
