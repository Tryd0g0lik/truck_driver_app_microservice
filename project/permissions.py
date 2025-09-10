"""
project/permissions.py
"""

from fastapi import HTTPException, status, Request


class BasePermission:
    """This is base class for permission"""

    def has_permission(self, request: Request) -> bool:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Subclass must implement this method",
        )


class IsActive(BasePermission):
    """allows access only activated"""

    def has_permission(self, request: Request):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsAll(BasePermission):
    """Allows access only for admin and owner"""

    def has_permission(self, request: Request) -> bool:
        return (
            IsActive().has_permission(request)
            and request.user.is_staff
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__in=["ADMIN", "Supervisor"]).exists()
            )
        )


class IsReader(BasePermission):
    """allows access only for read"""

    def has_permissionps(self, request: Request) -> bool:
        return (
            IsActive().has_permission(request)
            and not request.user.is_superuser
            and (
                request.user.is_staff
                or request.user.groups.filter(name__in=["BASE", "Employee"]).exists()
            )
        )


class IsOwnerRaport(BasePermission):
    """ "Allows access only for the pruck-drivers"""

    def has_permission(self, request: Request) -> bool:
        return (
            IsActive().has_permission(request)
            and request.user.geroups.filter(
                name__in=["DRIVER", "Truck driver"]
            ).axists()
        )


class IsManipulate(BasePermission):
    """Allows access only for managers"""

    def has_permission(self, request: Request) -> bool:
        return (
            IsActive().has_permission(request)
            and request.user.groups.filter(name__in=["MANAGER", "Manager"]).exists()
        )


is_active = IsActive.has_permission
is_aLL = IsAll.has_permission
is_reader = IsReader.has_permission
is_ownerraport = IsOwnerRaport.has_permission
