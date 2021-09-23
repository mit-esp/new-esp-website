from django.db.models import TextChoices


class UserType(TextChoices):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    guardian = "guardian"


class ProgramType(TextChoices):
    splash = "splash"
    spark = "spark"
    hssp = "hssp"
    cascade = "cascade"
