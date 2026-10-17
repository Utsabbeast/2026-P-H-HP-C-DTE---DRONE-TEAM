const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#password');
const eyeSlash = document.querySelector('#mama');

if (togglePassword && password && eyeSlash) {
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
}

// Toggle Login Views
function showLogin(role) {
    document.getElementById('role-selection').classList.add('hidden');
    document.getElementById('login-form-view').classList.remove('hidden');

    const isDgncc = (role === 'DGNCC Admin' || role === 'Admin');
    const titleText = isDgncc ? 'DGNCC Admin' : 'Unit Login';
    document.getElementById('login-title').innerText = titleText;

    const subtitle = document.getElementById('login-subtitle');
    const userInput = document.getElementById('usernameInput');
    const registerSection = document.getElementById('register-section');

    // Set a hidden field for login_type
    let form = document.querySelector('form');
    let loginTypeInput = form.querySelector('input[name="login_type"]');
    if (!loginTypeInput) {
        loginTypeInput = document.createElement('input');
        loginTypeInput.type = 'hidden';
        loginTypeInput.name = 'login_type';
        form.appendChild(loginTypeInput);
    }

    if (isDgncc) {
        loginTypeInput.value = 'atc';
        if (userInput) {
            userInput.placeholder = 'Username';
            userInput.value = 'admin';
        }
        if (subtitle) {
            subtitle.innerText = 'Authorized DGNCC Headquarters Access.';
        }
        if (registerSection) {
            registerSection.classList.remove('flex');
            registerSection.classList.add('hidden');
        }
    } else {
        loginTypeInput.value = 'pilot';
        if (userInput) {
            userInput.placeholder = 'Username';
            userInput.value = '';
        }
        if (subtitle) {
            subtitle.innerText = 'Log in with your official Unit Username and Password.';
        }
        if (registerSection) {
            registerSection.classList.remove('hidden');
            registerSection.classList.add('flex');
        }
    }
}

function guestLogin() {
    window.location.href = '/quick-login/guest/';
}

function showRoles() {
    document.getElementById('role-selection').classList.remove('hidden');
    document.getElementById('login-form-view').classList.add('hidden');
    // reset fields
    const form = document.querySelector('form');
    if (form) form.reset();
    if (password) password.setAttribute('type', 'password');
    if (togglePassword) togglePassword.classList.remove('hidden');
    if (eyeSlash) eyeSlash.classList.add('hidden');
    let msgBox = document.getElementById('inline-msg-box');
    if (msgBox) {
        msgBox.classList.add('hidden');
    }
}

// Ensure the page resets to Role Selection on refresh
document.addEventListener('DOMContentLoaded', function() {
    showRoles();
});
