from django.conf import settings


def constants(request):
    from common.constants import PermissionType
    return {
        "PermissionType": PermissionType,
    }


def localhost_context(request):
    return {'LOCALHOST': settings.LOCALHOST}
