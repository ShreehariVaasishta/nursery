from rest_framework.permissions import BasePermission


# Custom Permissions
class IsUser(BasePermission):
    def __init__(self, allowed_methods):
        super().__init__()
        self.allowed_methods = allowed_methods

    def has_permission(self, request, view):
        if request.user.user_type == "user":
            return True
        else:
            return False


class IsNursery(BasePermission):
    def __init__(self, allowed_methods):
        super().__init__()
        self.allowed_methods = allowed_methods

    def has_permission(self, request, view):
        if request.user.user_type == "nursery":
            return True
        else:
            return False