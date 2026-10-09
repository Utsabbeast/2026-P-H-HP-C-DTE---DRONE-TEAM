import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

overlay_css_and_html = '''    <style>
        #page-transition-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #f8fafc; z-index: 9999999;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            transition: opacity 0.5s ease-out; font-family: 'Inter', sans-serif;
        }
        .loader-text { margin-top: 30px; font-size: 1.25rem; font-weight: 700; color: #002D74; letter-spacing: 1px; text-transform: uppercase; }
        .loader { width: 112px; height: 112px; position: relative; }
        .box1, .box2, .box3 { box-sizing: border-box; position: absolute; display: block; }
        .box1 { border: 16px solid #002D74; width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; animation: abox1 4s 1s forwards ease-in-out infinite; }
        .box2 { border: 16px solid #dc2626; width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; animation: abox2 4s 1s forwards ease-in-out infinite; }
        .box3 { border: 16px solid #0ea5e9; width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; animation: abox3 4s 1s forwards ease-in-out infinite; }
        @keyframes abox1 { 0% { width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; } 12.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; } 25% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; } 37.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; } 50% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; } 62.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; } 75% { width: 48px; height: 112px; margin-top: 0px; margin-left: 0px; } 87.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } 100% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } }
        @keyframes abox2 { 0% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } 12.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } 25% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } 37.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; } 50% { width: 112px; height: 48px; margin-top: 0px; margin-left: 0px; } 62.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } 75% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } 87.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } 100% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } }
        @keyframes abox3 { 0% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } 12.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; } 25% { width: 48px; height: 112px; margin-top: 0px; margin-left: 64px; } 37.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; } 50% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; } 62.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; } 75% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; } 87.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; } 100% { width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; } }
    </style>
    <div id="page-transition-overlay">
        <div class="loader">
            <div class="box1"></div>
            <div class="box2"></div>
            <div class="box3"></div>
        </div>
        <div class="loader-text">Loading Dashboard...</div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                var overlay = document.getElementById('page-transition-overlay');
                overlay.style.opacity = '0';
                setTimeout(function() { overlay.remove(); }, 500);
            }, 1500); // 1.5 seconds loading overlay
        });
    </script>
'''

# insert right after <body> tag
content = re.sub(r'(<body.*?>)', r'\1\n' + overlay_css_and_html, content)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
