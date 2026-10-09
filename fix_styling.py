import os

def fix_history():
    path = r'c:\Users\kakol\OneDrive\Desktop\Coding\Drone\templates\history.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix CSS
    old_css = """    <style>
    body { background-color: #f8fafc; font-family: 'Outfit', sans-serif; }
    .history-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .history-title { color: #002D74; font-size: 1.8rem; font-weight: 800; border-bottom: 2px solid #002D74; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .requests-container { display: flex; flex-direction: column; align-items: center; }
    .history-table-container { background: #f0f7ff; border: 2px solid #002D74; box-shadow: 0 8px 16px -4px rgba(0,45,116,0.15); border-radius: 8px; overflow-x: auto; margin-bottom: 3rem; width: 100%; max-width: 1000px; padding: 1rem; }
    .history-table { width: 100%; border-collapse: collapse; text-align: left; }
    .history-table th { background-color: #002D74; color: #fff; padding: 1rem; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; }
    .history-table td { padding: 1rem; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 0.95rem; }
    .history-table tr:hover { background-color: #f1f5f9; }
</style>"""
    new_css = """    <style>
    body { background-color: #f8fafc; font-family: 'Outfit', sans-serif; }
    .requests-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .requests-title { color: #002D74; font-size: 1.8rem; font-weight: 800; border-bottom: 2px solid #002D74; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .requests-table-container { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 0; overflow-x: auto; margin-bottom: 3rem; }
    .requests-table { width: 100%; border-collapse: collapse; text-align: left; }
    .requests-table th { background-color: #002D74; color: #fff; padding: 1rem; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; }
    .requests-table td { padding: 1rem; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 0.95rem; }
    .requests-table tr:hover { background-color: #f1f5f9; }
    .status-badge { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 700; border-radius: 0; text-transform: uppercase; border: 1px solid; display: inline-block; }
    .status-PENDING { background-color: #fef3c7; color: #d97706; border-color: #d97706; }
    .status-APPROVED { background-color: #dcfce7; color: #15803d; border-color: #15803d; }
    .status-REJECTED { background-color: #fee2e2; color: #b91c1c; border-color: #b91c1c; }
</style>"""
    if old_css in content:
        content = content.replace(old_css, new_css)
    
    # Fix back button
    old_btn = '<a href="{% url \'telemetry:dashboard\' %}" class="btn btn-outline btn-sm">← Back to Dashboard</a>'
    new_btn = '<a href="{% url \'telemetry:dashboard\' %}" class="btn-underline">← Back to Dashboard</a>'
    if old_btn in content:
        content = content.replace(old_btn, new_btn)

    # Fix class names
    content = content.replace('class="history-container"', 'class="requests-container"')
    content = content.replace('class="history-title"', 'class="requests-title"')
    content = content.replace('class="history-table-container"', 'class="requests-table-container"')
    content = content.replace('class="history-table"', 'class="requests-table"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_status():
    path = r'c:\Users\kakol\OneDrive\Desktop\Coding\Drone\templates\status.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix CSS
    old_css = """    <style>
    body { background-color: #f8fafc; font-family: 'Outfit', sans-serif; }
    .status-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .status-title { color: #002D74; font-size: 1.8rem; font-weight: 800; border-bottom: 2px solid #002D74; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .status-table-container { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 0; overflow-x: auto; margin-bottom: 3rem; }
    .status-table { width: 100%; border-collapse: collapse; text-align: left; }
    .status-table th { background-color: #002D74; color: #fff; padding: 1rem; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; }
    .status-table td { padding: 1rem; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 0.95rem; }
    .status-table tr:hover { background-color: #f1f5f9; }
    .status-badge { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 700; border-radius: 0; text-transform: uppercase; border: 1px solid; display: inline-block; }
    .status-PENDING { background-color: #fef3c7; color: #d97706; border-color: #d97706; }
    .status-APPROVED { background-color: #dcfce7; color: #15803d; border-color: #15803d; }
    .status-REJECTED { background-color: #fee2e2; color: #b91c1c; border-color: #b91c1c; }
    .status-ACTIVE { background-color: #dbeafe; color: #1d4ed8; border-color: #1d4ed8; }
</style>"""
    new_css = """    <style>
    body { background-color: #f8fafc; font-family: 'Outfit', sans-serif; }
    .requests-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .requests-title { color: #002D74; font-size: 1.8rem; font-weight: 800; border-bottom: 2px solid #002D74; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .requests-table-container { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 0; overflow-x: auto; margin-bottom: 3rem; }
    .requests-table { width: 100%; border-collapse: collapse; text-align: left; }
    .requests-table th { background-color: #002D74; color: #fff; padding: 1rem; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; }
    .requests-table td { padding: 1rem; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 0.95rem; }
    .requests-table tr:hover { background-color: #f1f5f9; }
    .status-badge { padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: 700; border-radius: 0; text-transform: uppercase; border: 1px solid; display: inline-block; }
    .status-PENDING { background-color: #fef3c7; color: #d97706; border-color: #d97706; }
    .status-APPROVED { background-color: #dcfce7; color: #15803d; border-color: #15803d; }
    .status-REJECTED { background-color: #fee2e2; color: #b91c1c; border-color: #b91c1c; }
    .status-ACTIVE { background-color: #dbeafe; color: #1d4ed8; border-color: #1d4ed8; }
</style>"""
    if old_css in content:
        content = content.replace(old_css, new_css)
        
    # The back button is already correct in status.html: class="btn-underline"
    # Now replace classes
    content = content.replace('class="status-container"', 'class="requests-container"')
    content = content.replace('class="status-title"', 'class="requests-title"')
    content = content.replace('class="status-table-container"', 'class="requests-table-container"')
    content = content.replace('class="status-table"', 'class="requests-table"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_history()
fix_status()
print("history.html and status.html successfully updated to match requests.html CSS")
