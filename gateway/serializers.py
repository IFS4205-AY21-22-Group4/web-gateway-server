from rest_framework import serializers
from .models import Gateway, GatewayRecord


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = ("site_owner", "gateway_id", "authentication_token")


class GatewayRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayRecord
        fields = ("token", "gateway", "timestamp")
