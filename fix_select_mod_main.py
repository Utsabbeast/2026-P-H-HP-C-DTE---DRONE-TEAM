import sys

content = open('templates/dashboard.html', 'r', encoding='utf-8').read()

old_select_mod_main = """        if (mode === 'main') {
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
        } else if (mode === 'simulator') {"""

new_select_mod_main = """        if (mode === 'main') {
            if (window.setDashboardMode) window.setDashboardMode('main');
            if (mapTitle) mapTitle.innerText = "Main Mode (Overview)";
            if (mapRoute) mapRoute.innerText = "Overview";
        } else if (mode === 'simulator') {"""

content = content.replace(old_select_mod_main, new_select_mod_main)

open('templates/dashboard.html', 'w', encoding='utf-8').write(content)
print("Updated dashboard.html with window.setDashboardMode('main')")
