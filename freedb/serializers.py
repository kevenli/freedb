from rest_framework.serializers import ModelSerializer
from .models import Database


class DatabaseSerializer(ModelSerializer):
    class Meta:
        model = Database
        fields = ['name']