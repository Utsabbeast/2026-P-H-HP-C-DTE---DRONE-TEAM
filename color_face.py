import re

files = ['templates/dev_error.html', 'templates/404.html']

old_svg = '''              <svg class="face" viewBox="0 0 320 380">
                  <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="25">
                      <g class="face__eyes" transform="translate(0,112.5)">
                          <g transform="translate(15,0)">
                              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
                              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
                          </g>
                          <g transform="translate(230,0)">
                              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
                              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
                          </g>
                      </g>
                      <rect class="face__nose" x="132.5" y="112.5" width="55" height="155" rx="4" ry="4"></rect>
                      <g transform="translate(65,334)" stroke-dasharray="102 102">
                          <path class="face__mouth-left" d="M 0 30 C 0 30 40 0 95 0"></path>
                          <path class="face__mouth-right" d="M 95 0 C 150 0 190 30 190 30"></path>
                      </g>
                  </g>
              </svg>'''

new_svg = '''              <svg class="face" viewBox="0 0 320 380">
                  <g fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="25">
                      <g class="face__eyes" transform="translate(0,112.5)">
                          <!-- Left Eye (Red) -->
                          <g transform="translate(15,0)" stroke="#dc2626">
                              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
                              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
                          </g>
                          <!-- Right Eye (Navy Blue) -->
                          <g transform="translate(230,0)" stroke="#002D74">
                              <polyline class="face__eye-lid" points="37,0 0,120 75,120"></polyline>
                              <polyline class="face__pupil" points="55,120 55,155" stroke-dasharray="35 35"></polyline>
                          </g>
                      </g>
                      <!-- Nose (Light Blue) -->
                      <rect class="face__nose" x="132.5" y="112.5" width="55" height="155" rx="4" ry="4" stroke="#0ea5e9"></rect>
                      <!-- Mouth (Navy Blue) -->
                      <g transform="translate(65,334)" stroke-dasharray="102 102" stroke="#002D74">
                          <path class="face__mouth-left" d="M 0 30 C 0 30 40 0 95 0"></path>
                          <path class="face__mouth-right" d="M 95 0 C 150 0 190 30 190 30"></path>
                      </g>
                  </g>
              </svg>'''

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '<svg class="face" viewBox="0 0 320 380">' in content:
            # We use regex or string replace depending on exact spacing
            # Since there may be slight whitespace differences, I'll use regex to match the SVG block
            content = re.sub(r'<svg class="face" viewBox="0 0 320 380">.*?</svg>', new_svg, content, flags=re.DOTALL)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated SVG colors in {filepath}")
        else:
            print(f"Could not find SVG block in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
