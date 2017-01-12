from django.conf import settings
from rest_framework import permissions
from logging import getLogger

from .authentication import authenticate_admin

logger = getLogger('django')


class UserPermission(permissions.BasePermission):
    """Checks if valid user"""
    def has_permission(self, request, view):
        user = request.user
        return True
        # if hasattr(user, 'details'):
        #    return True
        # return False


class AdminPermission(permissions.BasePermission):
    """Checks admin token"""
    def has_permission(self, request, view):
        return authenticate_admin(getattr(settings, 'REHIVE_ADMIN_TOKEN'), request, view)