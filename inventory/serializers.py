from rest_framework import serializers
from .models import SnackItem

class SnackItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnackItem
        fields = '__all__' 