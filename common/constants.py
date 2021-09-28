from django.db.models import TextChoices


class UserType(TextChoices):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    guardian = "guardian"
    onsite_volunteer = "onsite_volunteer", "On-site Volunteer"
