import re

filepath = 'templates/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The button to remove:
btn_pattern = r'<button onclick="window\.open\(''https://docs\.google\.com/forms/d/e/1FAIpQLSfbUQWD-KAF8E2ID8c0Jux1FpspoCIsMZGJHMJGDYvBT8VKNA/viewform\?usp=sharing&amp;ouid=102528684174039826716'', ''_blank''\)" class="btn-96 btn-navy shadow-lg border border-gray-300" style="background: #10b981; color: white; border-color: #059669;"><span>Review Dashboard</span></button>'
btn_pattern_2 = r'<button onclick="window\.open\(''https://docs\.google\.com/forms/d/e/1FAIpQLSfbUQWD-KAF8E2ID8c0Jux1FpspoCIsMZGJHMJGDYvBT8VKNA/viewform\?usp=sharing&ouid=102528684174039826716'', ''_blank''\)" class="btn-96 btn-navy shadow-lg border border-gray-300" style="background: #10b981; color: white; border-color: #059669;"><span>Review Dashboard</span></button>'

if btn_pattern in content:
    content = content.replace(btn_pattern, "")
elif btn_pattern_2 in content:
    content = content.replace(btn_pattern_2, "")
else:
    # Try regex if exact match fails
    content = re.sub(r'<button onclick="window\.open\(''https://docs\.google\.com/forms/.*?><span>Review Dashboard</span></button>', '', content, flags=re.DOTALL)

# The new icon button to insert
icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-chat-left-text" viewBox="0 0 16 16">
  <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
  <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/>
</svg>"""

new_btn = f"""
          <!-- Review Icon Button -->
          <button onclick="window.open('https://docs.google.com/forms/d/e/1FAIpQLSfbUQWD-KAF8E2ID8c0Jux1FpspoCIsMZGJHMJGDYvBT8VKNA/viewform?usp=sharing&ouid=102528684174039826716', '_blank')" 
                  class="absolute bottom-4 left-4 bg-white text-[#002D74] border border-gray-300 shadow-md p-3 rounded-full hover:bg-gray-100 transition-colors z-50 group" 
                  title="Review">
              {icon_svg}
              <span class="absolute left-14 top-1/2 -translate-y-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">Review</span>
          </button>
"""

# Insert before the closing div of the white box
# The white box has class "bg-white border border-gray-200 flex w-full max-w-6xl mx-4 md:mx-12 p-6 items-center relative z-10 shadow-2xl rounded-sm"
# It ends right before `<a href="{% url 'telemetry:terms' %}"`
content = content.replace("</div>\n        <a href=\"{% url 'telemetry:terms' %}\"", new_btn + "        </div>\n        <a href=\"{% url 'telemetry:terms' %}\"")

# We should make sure we didn't miss replacing it
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
