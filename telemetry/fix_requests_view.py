import re

filepath = 'telemetry/views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = """class RequestsView(TemplateView):
    template_name = 'requests.html'"""

replacement = """class RequestsView(TemplateView):
    template_name = 'requests.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        return context"""

if pattern in content:
    content = content.replace(pattern, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated RequestsView to explicitly pass user_role")
else:
    print("Could not find pattern in views.py")
