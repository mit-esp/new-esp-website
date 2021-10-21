from common.constants import PermissionType, UserType
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


DEFAULT_ADMIN_PROGRAM_PERMISSIONS = [
    PermissionType.access_formstack,
    PermissionType.enter_program_lottery,
    PermissionType.register_for_program,
    PermissionType.teacher_submit_course,
    PermissionType.volunteer_program_dashboard_view,
    PermissionType.volunteer_program_signup,
]


DEFAULT_STUDENT_PERMISSIONS = [
    PermissionType.student_dashboard_view,
    PermissionType.update_profile,
]


DEFAULT_TEACHER_PERMISSIONS = [
    PermissionType.teacher_dashboard_view,
    PermissionType.update_profile,
]


def give_user_permissions(user, permissions, program=None, course=None, **kwargs):
    new_permissions = 0
    for permission in permissions:
        _permission, created = Permission.objects.update_or_create(
            user=user,
            permission_type=permission,
            program=program,
            course=course,
            defaults=kwargs
        )
        if created:
            new_permissions += 1
    return new_permissions


def give_user_type_permissions(user_type, permissions, program=None, course=None, **kwargs):
    new_permissions = 0
    for permission in permissions:
        _permission, created = Permission.objects.update_or_create(
            user_type=user_type,
            permission_type=permission,
            program=program,
            course=course,
            defaults=kwargs
        )
        if created:
            new_permissions += 1
    return new_permissions


def open_program_to_admins(program):
    return give_user_type_permissions(UserType.admin, permissions=DEFAULT_ADMIN_PROGRAM_PERMISSIONS, program=program)


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    permission_model = Permission
