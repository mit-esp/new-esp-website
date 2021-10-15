import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Now
from simple_history.models import HistoricalRecords

from common.constants import PermissionType, UserType
from common.managers import UserManager


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
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


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=False)  # allow users to register under different usernames and roles
    first_name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128, null=True)
    verified = models.BooleanField(default=True)
    user_type = models.CharField(max_length=128, choices=UserType.choices)

    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.username

    def get_dashboard_url(self):
        dashboard_url_mapping = {
            UserType.admin: "admin_dashboard",
            UserType.teacher: "teacher_dashboard",
            UserType.student: "student_dashboard",
            UserType.guardian: "guardian_dashboard",
            UserType.onsite_volunteer: "volunteer_dashboard",
        }
        return dashboard_url_mapping[self.user_type]


class BasePermission(BaseModel):
    # A permission can be assigned to a User or a user type
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permissions", null=True, blank=True)
    user_type = models.CharField(choices=UserType.choices, max_length=128, blank=True, null=True)

    permission_type = models.CharField(choices=PermissionType.choices, max_length=128)

    start_date = models.DateTimeField(default=Now, blank=True)
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        abstract = True
