import os

file_path = r'c:\Users\kakol\OneDrive\Desktop\Coding\Drone\templates\dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """                    <style>
                        .hamburger { cursor: pointer; display: flex; align-items: center; margin-left: 10px; }
                        .hamburger input { display: none; }
                        .hamburger svg { height: 38px; width: 38px; transition: transform 600ms cubic-bezier(0.4, 0, 0.2, 1); }
                        .hamburger .line { fill: none; stroke: #002D74; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5; transition: stroke-dasharray 600ms cubic-bezier(0.4, 0, 0.2, 1), stroke-dashoffset 600ms cubic-bezier(0.4, 0, 0.2, 1); }
                        .hamburger .line-top-bottom { stroke-dasharray: 12 63; }
                        .hamburger input:checked + svg { transform: rotate(-45deg); }
                        .hamburger input:checked + svg .line-top-bottom { stroke-dasharray: 20 300; stroke-dashoffset: -32.42; }
                    </style>
                    <label class="hamburger" onclick="toggleDropdown('modsDropdown', event)" title="Select Mode">
                        <input type="checkbox" id="hamburger-checkbox" />
                        <svg viewBox="0 0 32 32">
                            <path class="line line-top-bottom" d="M27 10 13 10C10.8 10 9 8.2 9 6 9 3.5 10.8 2 13 2 15.2 2 17 3.8 17 6L17 26C17 28.2 18.8 30 21 30 23.2 30 25 28.2 25 26 25 23.8 23.2 22 21 22L7 22"></path>
                            <path class="line" d="M7 16 27 16"></path>
                        </svg>
                    </label>"""

new_code = """                    <style>
                        .hamburger-btn { cursor: pointer; display: flex; align-items: center; gap: 6px; padding: 4px 12px; margin-left: 10px; color: #002D74; border: 2px solid #002D74; background: transparent; font-weight: 700; border-radius: 0; font-size: 0.85rem; height: 32px; transition: all 0.2s; }
                        .hamburger-btn:hover { background: #f1f5f9; }
                        .hamburger-btn input { display: none; }
                        .hamburger-btn svg { height: 20px; width: 20px; transition: transform 600ms cubic-bezier(0.4, 0, 0.2, 1); margin-top: 1px; }
                        .hamburger-btn .line { fill: none; stroke: #002D74; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5; transition: stroke-dasharray 600ms cubic-bezier(0.4, 0, 0.2, 1), stroke-dashoffset 600ms cubic-bezier(0.4, 0, 0.2, 1); }
                        .hamburger-btn .line-top-bottom { stroke-dasharray: 12 63; }
                        .hamburger-btn input:checked ~ svg { transform: rotate(-45deg); }
                        .hamburger-btn input:checked ~ svg .line-top-bottom { stroke-dasharray: 20 300; stroke-dashoffset: -32.42; }
                    </style>
                    <label class="hamburger-btn" onclick="toggleDropdown('modsDropdown', event)" title="Select Mode">
                        <span>Modes</span>
                        <input type="checkbox" id="hamburger-checkbox" />
                        <svg viewBox="0 0 32 32">
                            <path class="line line-top-bottom" d="M27 10 13 10C10.8 10 9 8.2 9 6 9 3.5 10.8 2 13 2 15.2 2 17 3.8 17 6L17 26C17 28.2 18.8 30 21 30 23.2 30 25 28.2 25 26 25 23.8 23.2 22 21 22L7 22"></path>
                            <path class="line" d="M7 16 27 16"></path>
                        </svg>
                    </label>"""

if old_code in content:
    content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated the Modes button styling.")
else:
    print("Could not find the old code block in dashboard.html.")
