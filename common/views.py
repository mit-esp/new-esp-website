from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")
