from django.db.models import TextChoices


class UserType(TextChoices):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    guardian = "guardian"
    onsite_volunteer = "onsite_volunteer", "On-site Volunteer"


class PermissionType(TextChoices):
    # WIP: permissions list TBD
    view_courses = "view_courses"
    edit_courses = "edit_courses"
    view_all_programs = "view_all_programs"
    edit_programs = "edit_programs"
    view_student_dashboard = "view_student_dashboard"
    view_all_student_dashboards = "view_all_student_dashboards"
    view_teacher_dashboard = "view_teacher_dashboard"
    view_all_teacher_dashboards = "view_all_teacher_dashboards"
