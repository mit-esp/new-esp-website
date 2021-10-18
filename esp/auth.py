from common.constants import PermissionType
from common.views import BasePermissionRequiredMixin
from esp.models.program import Permission

DEFAULT_ADMIN_PERMISSIONS = [
    PermissionType.admin_dashboard_view,
    PermissionType.courses_edit,
    PermissionType.courses_view_all,
    PermissionType.programs_edit,
    PermissionType.programs_view_all,
    PermissionType.student_dashboard_view,
    PermissionType.teacher_dashboard_view,
]


DEFAULT_STUDENT_PERMISSIONS = [
    PermissionType.student_dashboard_view,
    PermissionType.update_profile,
]


DEFAULT_TEACHER_PERMISSIONS = [
    PermissionType.teacher_dashboard_view,
    PermissionType.update_profile,
]


def give_user_permissions(user, permissions, **kwargs):
    new_permissions = 0
    for permission in permissions:
        _permission, created = Permission.objects.update_or_create(
            user=user,
            permission_type=permission,
            defaults=kwargs
        )
        if created:
            new_permissions += 1
    return new_permissions


def give_user_type_permissions(user_type, permissions, **kwargs):
    new_permissions = 0
    for permission in permissions:
        _permission, created = Permission.objects.update_or_create(
            user_type=user_type,
            permission_type=permission,
            defaults=kwargs
        )
        if created:
            new_permissions += 1
    return new_permissions


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    permission_model = Permission
