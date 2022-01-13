def constants(request):
    from common.constants import UserType, PermissionType
    return {
        "PermissionType": PermissionType,
        "UserType": UserType,
    }
