from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SnackItem
from .serializers import SnackItemSerializer
from rest_framework.permissions import BasePermission

class IsStaffMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff_member

# Create your views here.

class SnackItemViewSet(viewsets.ModelViewSet):
    queryset = SnackItem.objects.all()
    serializer_class = SnackItemSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStaffMember]
        return [permission() for permission in permission_classes]
