import os

auto_logout_script = """
    // Auto logout on refresh
    if (performance.getEntriesByType("navigation").length > 0 && performance.getEntriesByType("navigation")[0].type === "reload") {
        window.location.replace("/logout/");
    }
"""

templates = [
    'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/dashboard.html',
    'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/requests.html',
    'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/status.html',
    'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/history.html',
    'c:/Users/kakol/OneDrive/Desktop/Coding/Drone/templates/mobile_dashboard.html',
]

for tmpl in templates:
    if os.path.exists(tmpl):
        with open(tmpl, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Auto logout on refresh" not in content:
            # Insert script right after <head> or at top of body
            if "<head>" in content:
                content = content.replace("<head>", "<head>\n<script>\n" + auto_logout_script + "\n</script>")
            else:
                content = "<script>\n" + auto_logout_script + "\n</script>\n" + content
            
            with open(tmpl, 'w', encoding='utf-8') as f:
                f.write(content)
        print(f"Updated {tmpl}")
