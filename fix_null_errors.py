import re

filepath = 'static/js/dashboard.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Instead of complex regex, I will just do a string replacement for the function updateConnectionStatus.
# First, let's extract the function.
start_idx = content.find('function updateConnectionStatus(isConnected, secondsAgo, customLabel) {')
end_idx = content.find('// Polling Logic', start_idx)

original_func = content[start_idx:end_idx]

# We need to replace all assignments to `elements.connectionStatusPill...`, `elements.statusDot...`, `elements.statusLabel...`
# with safe access.

new_func = original_func
# Let's replace the block in simulator
new_func = new_func.replace(
'''        if (activeMode === 'simulator') {
            elements.connectionStatusPill.className = 'connection-status connected';
            elements.statusDot.className = 'status-indicator-dot dot-green';
            elements.statusLabel.textContent = '✈️ Simulation Connected';''',
'''        if (activeMode === 'simulator') {
            if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
            if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
            if (elements.statusLabel) elements.statusLabel.textContent = '✈️ Simulation Connected';'''
)

# Phone Connected
new_func = new_func.replace(
'''                // 📱 Phone Connected
                elements.connectionStatusPill.className = 'connection-status connected';
                elements.statusDot.className = 'status-indicator-dot dot-green';
                elements.statusLabel.textContent = '📱 Phone Connected';

                elements.statusConnBadge.className = 'item-value-pill pill-green';
                elements.statusConnDot.className = 'dot-indicator dot-green';
                elements.statusConnText.textContent = '📱 Phone Connected';
                elements.statusConnHint.textContent = `Live GPS packets active (${secText})`;''',
'''                // 📱 Phone Connected
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
                if (elements.statusLabel) elements.statusLabel.textContent = '📱 Phone Connected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = '📱 Phone Connected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = `Live GPS packets active (${secText})`;'''
)

# Phone Disconnected
new_func = new_func.replace(
'''                // 📵 Phone Disconnected
                elements.connectionStatusPill.className = 'connection-status disconnected';
                elements.statusDot.className = 'status-indicator-dot dot-red';
                elements.statusLabel.textContent = '📵 Phone Disconnected';

                elements.statusConnBadge.className = 'item-value-pill';
                elements.statusConnDot.className = 'dot-indicator dot-red';
                elements.statusConnText.textContent = '📵 Phone Disconnected';
                elements.statusConnHint.textContent = `No GPS updates (${secText}). Coordinates frozen. Check /mobile/`;''',
'''                // 📵 Phone Disconnected
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status disconnected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-red';
                if (elements.statusLabel) elements.statusLabel.textContent = '📵 Phone Disconnected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-red';
                if (elements.statusConnText) elements.statusConnText.textContent = '📵 Phone Disconnected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = `No GPS updates (${secText}). Coordinates frozen. Check /mobile/`;'''
)

# Drone Connected
new_func = new_func.replace(
'''            // Drone Mode (ESP32 Hardware)
            if (isConnected) {
                elements.connectionStatusPill.className = 'connection-status connected';
                elements.statusDot.className = 'status-indicator-dot dot-green';
                elements.statusLabel.textContent = 'Drone Connected (ESP32 Live)';

                elements.statusConnBadge.className = 'item-value-pill pill-green';
                elements.statusConnDot.className = 'dot-indicator dot-green';
                elements.statusConnText.textContent = 'ESP32 Broadcasting';
                elements.statusConnHint.textContent = 'Hardware online';''',
'''            // Drone Mode (ESP32 Hardware)
            if (isConnected) {
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status connected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-green';
                if (elements.statusLabel) elements.statusLabel.textContent = 'Drone Connected (ESP32 Live)';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill pill-green';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-green';
                if (elements.statusConnText) elements.statusConnText.textContent = 'ESP32 Broadcasting';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Hardware online';'''
)

# Drone Disconnected
new_func = new_func.replace(
'''            } else {
                elements.connectionStatusPill.className = 'connection-status disconnected';
                elements.statusDot.className = 'status-indicator-dot dot-red';
                elements.statusLabel.textContent = 'Drone Not Connected';

                elements.statusConnBadge.className = 'item-value-pill';
                elements.statusConnDot.className = 'dot-indicator dot-red';
                elements.statusConnText.textContent = 'Disconnected';
                elements.statusConnHint.textContent = 'Awaiting ESP32 packet';
            }''',
'''            } else {
                if (elements.connectionStatusPill) elements.connectionStatusPill.className = 'connection-status disconnected';
                if (elements.statusDot) elements.statusDot.className = 'status-indicator-dot dot-red';
                if (elements.statusLabel) elements.statusLabel.textContent = 'Drone Not Connected';

                if (elements.statusConnBadge) elements.statusConnBadge.className = 'item-value-pill';
                if (elements.statusConnDot) elements.statusConnDot.className = 'dot-indicator dot-red';
                if (elements.statusConnText) elements.statusConnText.textContent = 'Disconnected';
                if (elements.statusConnHint) elements.statusConnHint.textContent = 'Awaiting ESP32 packet';
            }'''
)

content = content[:start_idx] + new_func + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added null checks to updateConnectionStatus")
