import sys

loader_html = """
    <!-- Full Page Loader -->
    <div id="page-loader" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #002D74; z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: opacity 0.5s ease, visibility 0.5s ease;">
        <div style="position: relative; width: 80px; height: 80px;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 4px solid rgba(255,255,255,0.1); border-radius: 50%;"></div>
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 4px solid transparent; border-top-color: #0ea5e9; border-radius: 50%; animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;"></div>
            <div style="position: absolute; top: 15px; left: 15px; width: 50px; height: 50px; border: 4px solid transparent; border-bottom-color: #fff; border-radius: 50%; animation: spin 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite reverse;"></div>
        </div>
        <div style="color: white; margin-top: 24px; font-family: 'Outfit', sans-serif; font-weight: 700; letter-spacing: 0.2em; font-size: 14px; animation: pulse 2s infinite;">INITIALIZING...</div>
    </div>
    <style>
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
    <script>
        window.addEventListener('load', function() {
            const loader = document.getElementById('page-loader');
            if (loader) {
                // Ensure loader shows for at least a brief moment for transition effect
                setTimeout(() => {
                    loader.style.opacity = '0';
                    loader.style.visibility = 'hidden';
                }, 400);
            }
        });
        
        // Also show loader on beforeunload to simulate 'in-between' transition
        window.addEventListener('beforeunload', function() {
            const loader = document.getElementById('page-loader');
            if (loader) {
                loader.style.visibility = 'visible';
                loader.style.opacity = '1';
            }
        });
    </script>
"""

def add_loader(filepath):
    content = open(filepath, 'r', encoding='utf-8').read()
    if 'id="page-loader"' in content:
        print(f"Loader already in {filepath}")
        return
        
    # find body tag and insert right after
    body_tag_index = content.find('<body')
    if body_tag_index != -1:
        # find end of body tag
        end_of_body_tag = content.find('>', body_tag_index) + 1
        content = content[:end_of_body_tag] + loader_html + content[end_of_body_tag:]
        open(filepath, 'w', encoding='utf-8').write(content)
        print(f"Added loader to {filepath}")
    else:
        print(f"Could not find body tag in {filepath}")

add_loader('templates/login.html')
add_loader('templates/dashboard.html')
