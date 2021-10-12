from rest_framework import serializers
from .models import Gateway, GatewayRecord


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = ("id", "site_owner", "gateway_id", "authentication_token")


class GatewayRecordSerializer(serializers.Serializer):
    token_uuid = serializers.CharField(max_length=36)
    gateway_id = serializers.CharField(max_length=15)
