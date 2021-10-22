from django.core.management import BaseCommand

from common.constants import UserType
from esp.auth import (DEFAULT_ADMIN_PERMISSIONS, DEFAULT_STUDENT_PERMISSIONS,
                      DEFAULT_TEACHER_PERMISSIONS, give_user_type_permissions)


class Command(BaseCommand):
    help = "Sets up default user group permissions"

    def handle(self, *args, **options):
        new_permissions = 0
        new_permissions += give_user_type_permissions(UserType.admin, DEFAULT_ADMIN_PERMISSIONS)
        new_permissions += give_user_type_permissions(UserType.student, DEFAULT_STUDENT_PERMISSIONS)
        new_permissions += give_user_type_permissions(UserType.teacher, DEFAULT_TEACHER_PERMISSIONS)
        self.stdout.write(f"{new_permissions} new permissions created.")
