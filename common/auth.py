from common.constants import PermissionType, UserType

ADMIN_PERMISSIONS = [
    PermissionType.admin_dashboard_actions,
    PermissionType.admin_dashboard_view,
    PermissionType.courses_edit_all,
    PermissionType.courses_view_all,
    PermissionType.programs_edit_all,
    PermissionType.programs_view_all,
    PermissionType.run_program_lottery,
    PermissionType.use_scheduler,
    PermissionType.send_email,
    PermissionType.student_create_profile,
    PermissionType.student_dashboard_view,
    PermissionType.student_profiles_edit_all,
    PermissionType.student_register_for_program,
    PermissionType.student_registrations_edit_all,
    PermissionType.student_update_profile,
    PermissionType.teacher_create_profile,
    PermissionType.teacher_dashboard_view,
    PermissionType.teacher_register_for_program,
    PermissionType.teacher_edit_own_courses,
    PermissionType.teacher_profiles_edit_all,
    PermissionType.teacher_registrations_edit_all,
    PermissionType.teacher_update_profile,
    PermissionType.volunteer_program_dashboard_view,
    PermissionType.volunteer_register_for_program,
]


STUDENT_PERMISSIONS = [
    PermissionType.student_create_profile,
    PermissionType.student_dashboard_view,
    PermissionType.student_update_profile,
    PermissionType.student_register_for_program,
]


TEACHER_PERMISSIONS = [
    PermissionType.teacher_create_profile,
    PermissionType.teacher_update_profile,
    PermissionType.teacher_dashboard_view,
    PermissionType.teacher_register_for_program,
    PermissionType.teacher_edit_own_courses,
]


VOLUNTEER_PERMISSIONS = [
    PermissionType.volunteer_program_dashboard_view,
    PermissionType.volunteer_register_for_program,
]


USER_TYPE_PERMISSIONS = {
    UserType.admin: ADMIN_PERMISSIONS,
    UserType.student: STUDENT_PERMISSIONS,
    UserType.teacher: TEACHER_PERMISSIONS,
    UserType.onsite_volunteer: VOLUNTEER_PERMISSIONS,
}
