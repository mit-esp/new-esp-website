from common.views import BasePermissionRequiredMixin
from esp.models.program import Permission


def give_user_permissions(user, permissions, start_date=None, end_date=None):
    for permission in permissions:
        Permission.objects.update_or_create(
            user=user,
            permission_type=permission,
            defaults={
                "start_date": start_date,
                "end_date": end_date
            }
        )


def give_user_type_permissions(user_type, permissions, start_date=None, end_date=None):
    for permission in permissions:
        Permission.objects.update_or_create(
            user_type=user_type,
            permission_type=permission,
            defaults={
                "start_date": start_date,
                "end_date": end_date
            }
        )


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    permission_model = Permission
