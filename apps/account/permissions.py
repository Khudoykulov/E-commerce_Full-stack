from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Faqatgina admin foydalanuvchilar o'zgartirish huquqiga ega,
    boshqa foydalanuvchilar faqat o'qish huquqiga ega.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff