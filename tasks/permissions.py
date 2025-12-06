from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Object-level permission to allow only owners to access objects.
    Assumes model instance has `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
