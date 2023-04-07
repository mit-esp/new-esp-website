import uuid

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from common.auth import USER_TYPE_PERMISSIONS
from common.constants import UserType
from common.managers import UserManager


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # created_on and updated_on are intended only for database audits.
    # Timestamps used in business logic should be added explicitly.
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)
    history = HistoricalRecords(inherit=True)

    def update(self, update_dict=None, **kwargs):
        """ Helper method to update objects """
        if not update_dict:
            update_dict = kwargs
        update_fields = {"updated_on"}
        for k, v in update_dict.items():
            setattr(self, k, v)
            update_fields.add(k)
        self.save(update_fields=update_fields)

    class Meta:
        abstract = True


class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.-]+\Z'
    message = (
        'Enter a valid username. This value may contain only letters, '
        'numbers, periods, underscores, asterisks, and dashes.'
    )
    flags = 0


class User(AbstractUser, BaseModel):
    username_validator = UsernameValidator()

    username = models.CharField(
        ('username'),
        max_length=30,
        unique=True,
        help_text=('Required. 30 characters or fewer. Letters, digits, periods, underscores, asterisks, and dashes only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )

    email = models.EmailField(unique=False)  # allow users to register under different usernames and roles
    first_name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128, null=True)
    verified = models.BooleanField(default=True)
    user_type = models.CharField(max_length=128, choices=UserType.choices)

    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def name(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_dashboard_url(self):
        dashboard_url_mapping = {
            UserType.admin: "admin_dashboard",
            UserType.teacher: "teacher_dashboard",
            UserType.student: "student_dashboard",
            UserType.guardian: "guardian_dashboard",
            UserType.onsite_volunteer: "volunteer_dashboard",
        }
        return dashboard_url_mapping[self.user_type]

    def has_permission(self, permission):
        return permission in USER_TYPE_PERMISSIONS[self.user_type]


class SiteRedirectPath(BaseModel):
    path = models.CharField(max_length=256, unique=True)
    redirect_url_name = models.CharField(
        max_length=256, null=True, blank=True,
        help_text="Must be a valid path name. Will be overridden if full url is set."
    )
    redirect_full_url = models.CharField(
        max_length=256, null=True, blank=True,
        help_text="May be either an absolute (external) URL or site path."
    )

    def get_redirect_url(self):
        return self.redirect_full_url if self.redirect_full_url else reverse(self.redirect_url_name)

    def __str__(self):
        return f"{self.path} -> {self.get_redirect_url()}"
