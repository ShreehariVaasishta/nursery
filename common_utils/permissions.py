from rest_framework.permissions import BasePermission


# Custom Permissions
class IsBuyerUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == "buyer":
            return True
        else:
            return False


class IsNurseryUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == "nursery":
            return True
        else:
            return False