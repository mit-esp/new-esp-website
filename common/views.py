from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic.base import TemplateView, View


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


class BasePermissionRequiredMixin(UserPassesTestMixin):
    permission = None  # Views which inherit from this mixin must set a permission.
    permission_model = None  # Set permission model to the app-specific BasePermission subclass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.permission:
            raise ImproperlyConfigured("No permissions set")
        if not self.permission_model:
            raise ImproperlyConfigured("No permission model set")

    def test_func(self):
        return self.get_permission_queryset().exists()

    def get_permission_queryset(self):
        return (
            self.permission_model.objects
                .filter(self.get_permission_applies_to_view_filter())
                .filter(self.get_permission_applies_to_user_filter())
        )

    def get_permission_applies_to_view_filter(self):
        # Should return Q object that represents whether a Permission object applies to the current view.
        return Q(
            Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True),
            start_date__lte=timezone.now(),
            permission_type=self.permission,
        )

    def get_permission_applies_to_user_filter(self):
        # Should return Q object that represents whether a Permission object applies to the current user.
        return Q(
            Q(user=self.request.user) | Q(user_type=self.request.user_type),
        )
