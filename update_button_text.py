with open('c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add centerBtnText reference
if "const centerBtnText = document.getElementById('centerButtonText');" not in content:
    content = content.replace("const mapTitle = document.getElementById('mapMainTitle');", 
                              "const mapTitle = document.getElementById('mapMainTitle');\n        const centerBtnText = document.getElementById('centerButtonText');")

# Update centerBtnText for main mode
if "centerBtnText.innerText = \"Center Map\";" not in content:
    content = content.replace("if (mapRoute) mapRoute.innerText = \"Overview\";", 
                              "if (mapRoute) mapRoute.innerText = \"Overview\";\n            if (centerBtnText) centerBtnText.innerText = \"Center Map\";")

# Update centerBtnText for simulator mode
if "centerBtnText.innerText = \"Center Simulator\";" not in content and "centerBtnText.innerText = \"Center Drone\";" not in content:
    content = content.replace("if (mapRoute) mapRoute.innerText = \"Simulator\";", 
                              "if (mapRoute) mapRoute.innerText = \"Simulator\";\n            if (centerBtnText) centerBtnText.innerText = \"Center Drone\";")

# Update centerBtnText for phone mode
if "centerBtnText.innerText = \"Center Phone\";" not in content:
    content = content.replace("if (mapRoute) mapRoute.innerText = \"Source: Android Phone\";", 
                              "if (mapRoute) mapRoute.innerText = \"Source: Android Phone\";\n            if (centerBtnText) centerBtnText.innerText = \"Center Phone\";")

# Update centerBtnText for drone mode
if "centerBtnText.innerText = \"Center Drone\";" not in content:
    content = content.replace("if (mapRoute) mapRoute.innerText = \"Source: Drone ESP32\";", 
                              "if (mapRoute) mapRoute.innerText = \"Source: Drone ESP32\";\n            if (centerBtnText) centerBtnText.innerText = \"Center Drone\";")

with open('c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
