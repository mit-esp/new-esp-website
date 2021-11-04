from django import template

register = template.Library()


@register.filter
def has_permission(user, permission):
    return user.has_permission(permission)
