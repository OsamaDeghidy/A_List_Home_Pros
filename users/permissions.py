from rest_framework import permissions
from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsAListHomePro(permissions.BasePermission):
    """
    Permission check for A-List Home Pro users.
    Note: Internally still uses UserRole.CONTRACTOR for backward compatibility.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.CONTRACTOR


class IsClient(permissions.BasePermission):
    """
    Permission check for client users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.CLIENT


class IsCrew(permissions.BasePermission):
    """
    Permission check for crew users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.CREW


class IsSpecialist(permissions.BasePermission):
    """
    Permission check for specialist users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.SPECIALIST


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can edit any object
        if request.user.role == UserRole.ADMIN:
            return True
            
        # Check if the object has a user attribute that matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If the object is a user, check if it's the same user
        return obj == request.user
