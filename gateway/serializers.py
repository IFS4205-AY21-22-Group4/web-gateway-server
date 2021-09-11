from rest_framework import serializers
from .models import Gateway


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = ("site_owner", "gateway_id", "authentication_token")
