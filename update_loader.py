import os

old_loader = """    <!-- Full Page Loader -->
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
    </style>"""

new_loader = """    <!-- Full Page Loader -->
    <div id="page-loader" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #ffffff; z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: opacity 0.5s ease, visibility 0.5s ease;">
        <div class="loader">
          <div class="box1"></div>
          <div class="box2"></div>
          <div class="box3"></div>
        </div>
        <div style="color: #002D74; margin-top: 40px; font-family: 'Outfit', sans-serif; font-weight: 700; letter-spacing: 0.2em; font-size: 14px; animation: pulse 2s infinite;">INITIALIZING...</div>
    </div>
    <style>
        .loader { width: 112px; height: 112px; }
        .box1, .box2, .box3 { box-sizing: border-box; position: absolute; display: block; }
        .box1 { width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; animation: abox1 4s 1s forwards ease-in-out infinite; border: 16px solid #002D74; }
        .box2 { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; animation: abox2 4s 1s forwards ease-in-out infinite; border: 16px solid #dc2626; }
        .box3 { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; animation: abox3 4s 1s forwards ease-in-out infinite; border: 16px solid #0ea5e9; }
        @keyframes abox1 {
          0% { width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; }
          12.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; }
          25% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; }
          37.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; }
          50% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; }
          62.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 0px; }
          75% { width: 48px; height: 112px; margin-top: 0px; margin-left: 0px; }
          87.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
          100% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
        }
        @keyframes abox2 {
          0% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
          12.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
          25% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
          37.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 0px; }
          50% { width: 112px; height: 48px; margin-top: 0px; margin-left: 0px; }
          62.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
          75% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
          87.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
          100% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
        }
        @keyframes abox3 {
          0% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
          12.5% { width: 48px; height: 48px; margin-top: 0px; margin-left: 64px; }
          25% { width: 48px; height: 112px; margin-top: 0px; margin-left: 64px; }
          37.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; }
          50% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; }
          62.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; }
          75% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; }
          87.5% { width: 48px; height: 48px; margin-top: 64px; margin-left: 64px; }
          100% { width: 112px; height: 48px; margin-top: 64px; margin-left: 0px; }
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>"""

files_to_update = [
    r'c:\Users\kakol\OneDrive\Desktop\Coding\Drone\templates\login.html',
    r'c:\Users\kakol\OneDrive\Desktop\Coding\Drone\templates\dashboard.html'
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_loader in content:
            content = content.replace(old_loader, new_loader)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated loader in {os.path.basename(filepath)}")
        else:
            print(f"Loader not found in {os.path.basename(filepath)}")
    else:
        print(f"File not found: {filepath}")
