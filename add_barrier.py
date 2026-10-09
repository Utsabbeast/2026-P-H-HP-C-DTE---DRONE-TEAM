import os

file_path = 'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update popstate logic
old_popstate = """    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.mode) {
            selectMod(event.state.mode, null, true);
        } else {
            // Check hash
            if (location.hash) {
                selectMod(location.hash.replace('#', ''), null, true);
            } else {
                selectMod('test_phone', null, true);
            }
        }
    });"""

new_popstate = """    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.mode) {
            selectMod(event.state.mode, null, true);
        } else if (event.state && event.state.barrier) {
            // Hit the barrier! Stay on dashboard by pushing the mode back to history.
            const currentMode = location.hash ? location.hash.replace('#', '') : 'main';
            history.pushState({mode: currentMode}, '', location.pathname + '#' + currentMode);
        } else {
            // Default fallback
            if (location.hash) {
                selectMod(location.hash.replace('#', ''), null, true);
            } else {
                selectMod('main', null, true);
            }
        }
    });"""

if old_popstate in content:
    content = content.replace(old_popstate, new_popstate)

# 2. Update initialization logic
old_init_1 = """    {% if request.session.user_role == 'ATC' %}
    document.addEventListener("DOMContentLoaded", function() {
        if (location.hash) {
            const currentMode = location.hash.replace('#', '');
            selectMod(currentMode, null, true);
            history.replaceState({mode: currentMode}, '', location.pathname + '#' + currentMode);
        } else {
            selectMod('main', null, true);
            history.replaceState({mode: 'main'}, '', location.pathname + '#main');
        }
    });
    {% else %}
    document.addEventListener("DOMContentLoaded", function() {
        if (location.hash) {
            const currentMode = location.hash.replace('#', '');
            selectMod(currentMode, null, true);
            history.replaceState({mode: currentMode}, '', location.pathname + '#' + currentMode);
        } else {
            selectMod('main', null, true);
            history.replaceState({mode: 'main'}, '', location.pathname + '#main');
        }
    });
    {% endif %}"""

new_init = """    document.addEventListener("DOMContentLoaded", function() {
        // Create a barrier history state so the user cannot use the back button to reach the login page
        if (!history.state || !history.state.barrier) {
            history.replaceState({barrier: true}, '', location.pathname);
            
            const initialMode = location.hash ? location.hash.replace('#', '') : 'main';
            history.pushState({mode: initialMode}, '', location.pathname + '#' + initialMode);
            selectMod(initialMode, null, true);
        } else {
            // If barrier already exists, just load mode
            const currentMode = location.hash ? location.hash.replace('#', '') : 'main';
            selectMod(currentMode, null, true);
        }
    });"""

if old_init_1 in content:
    content = content.replace(old_init_1, new_init)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dashboard.html with back button barrier.")
