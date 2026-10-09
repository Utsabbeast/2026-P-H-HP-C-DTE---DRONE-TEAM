import re

with open('templates/loading.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove meta refresh
content = re.sub(r'<meta http-equiv="refresh".*?>', '', content)

# Add js replace
js = '''
    <script>
        setTimeout(function() {
            window.location.replace("{% url 'telemetry:dashboard' %}");
        }, 2500);
    </script>
</head>
'''
content = content.replace('</head>', js)

with open('templates/loading.html', 'w', encoding='utf-8') as f:
    f.write(content)
