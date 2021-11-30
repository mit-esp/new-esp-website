from django.conf import settings
from django import template

register = template.Library()

def constants(request):
    from common.constants import PermissionType
    return {
        "PermissionType": PermissionType,
    }


@register.simple_tag
def django_setting(setting_name):
    return getattr(settings, setting_name, "")
