from django.conf import settings
from django import template

register = template.Library()


@register.filter
def has_permission(user, permission):
    return user.has_permission(permission)


@register.simple_tag
def django_setting(setting_name):
    return getattr(settings, setting_name, "")
