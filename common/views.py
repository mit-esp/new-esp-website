from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


class PermissionRequiredMixin(UserPassesTestMixin):
    permission = None  # Views which inherit from this mixin must set a permission.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.permission:
            raise NotImplementedError("No permissions set")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.user_has_permission() and self.permission_enabled_for_view()

    def user_has_permission(self):
        return self.request.user.has_permission(self.permission)

    def permission_enabled_for_view(self):
        # Override for views that are only enabled given certain database state
        return True
