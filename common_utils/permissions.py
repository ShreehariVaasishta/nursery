from rest_framework.permissions import BasePermission


# Custom Permissions
class IsBuyerUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.IsBuyer:
            return True
        else:
            return False


class IsNurseryUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.IsNursery:
            return True
        else:
            return False