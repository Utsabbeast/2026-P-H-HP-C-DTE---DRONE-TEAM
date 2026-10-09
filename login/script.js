function selectLogin(type) {
    document.querySelector('.login-options').classList.add('hidden');
    document.getElementById('login-form-area').classList.remove('hidden');
    document.getElementById('login-title').innerText = type + ' Login';
}

function goBack() {
    document.querySelector('.login-options').classList.remove('hidden');
    document.getElementById('login-form-area').classList.add('hidden');
    document.getElementById('loginForm').reset();
}

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Authentication initiated for ' + document.getElementById('login-title').innerText);
});
