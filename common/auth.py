from common.constants import PermissionType, UserType

ADMIN_PERMISSIONS = [
    PermissionType.student_create_profile,
    PermissionType.update_profile,
    PermissionType.access_formstack,
    PermissionType.admin_dashboard_view,
    PermissionType.courses_edit,
    PermissionType.courses_view_all,
    PermissionType.enter_program_lottery,
    PermissionType.programs_edit,
    PermissionType.programs_view_all,
    PermissionType.register_for_program,
    PermissionType.student_dashboard_view,
    PermissionType.teacher_create_profile,
    PermissionType.teacher_update_profile,
    PermissionType.teacher_dashboard_view,
    PermissionType.teacher_submit_course,
]


STUDENT_PERMISSIONS = [
    PermissionType.student_create_profile,
    PermissionType.student_dashboard_view,
    PermissionType.update_profile,
]


TEACHER_PERMISSIONS = [
    PermissionType.teacher_create_profile,
    PermissionType.teacher_update_profile,
    PermissionType.teacher_dashboard_view,
    PermissionType.update_profile,
]


VOLUNTEER_PERMISSIONS = [
    PermissionType.volunteer_program_dashboard_view,
    PermissionType.volunteer_program_signup,
]


USER_TYPE_PERMISSIONS = {
    UserType.admin: ADMIN_PERMISSIONS,
    UserType.student: STUDENT_PERMISSIONS,
    UserType.teacher: TEACHER_PERMISSIONS,
    UserType.onsite_volunteer: VOLUNTEER_PERMISSIONS,
}
