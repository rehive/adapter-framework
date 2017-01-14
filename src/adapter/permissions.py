from django.conf import settings
from rest_framework import permissions
from logging import getLogger

from .authentication import authenticate_admin

logger = getLogger('django')


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
           return True


class AdminPermission(permissions.BasePermission):
    """Checks admin token"""
    def has_permission(self, request, view):
        return authenticate_admin(getattr(settings, 'REHIVE_ADMIN_TOKEN'), request, view)