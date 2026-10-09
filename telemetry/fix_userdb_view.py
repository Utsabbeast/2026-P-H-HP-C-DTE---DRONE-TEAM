import re

filepath = 'telemetry/views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = """class UserDatabaseView(TemplateView):
    template_name = 'user_database.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_role') != 'ADMIN':
            return redirect('telemetry:dev-error')
        return super().dispatch(request, *args, **kwargs)"""

replacement = """class UserDatabaseView(TemplateView):
    template_name = 'user_database.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.session.get('user_role') != 'ATC':
            return redirect('telemetry:dev-error')
        return super().dispatch(request, *args, **kwargs)"""

if pattern in content:
    content = content.replace(pattern, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated UserDatabaseView logic in views.py")
else:
    print("Could not find pattern in views.py")
