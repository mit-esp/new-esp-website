def constants(request):
    from common.constants import PermissionType
    return {
        "PermissionType": PermissionType,
    }
