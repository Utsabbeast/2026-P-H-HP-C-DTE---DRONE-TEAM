from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import redirect

class UserDatabaseView(TemplateView):
    template_name = 'user_database.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_role') != 'ADMIN':
            return redirect('telemetry:dev-error')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('-date_joined')
        return context
