from rest_framework import serializers
from .models import Gateway, GatewayRecord, Token


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = ("id", "site_owner", "gateway_id", "authentication_token")


class GatewayRecordSerializer(serializers.Serializer):
    token_uuid = serializers.CharField(max_length=36)
    gateway_id = serializers.CharField(max_length=15)


class TokenSerializer(serializers.ModelSerializer):
    nric = serializers.ReadOnlyField(source="owner.nric")

    class Meta:
        model = Token
        fields = ("token_uuid", "nric")

    def to_representation(self, data):
        data = super(TokenSerializer, self).to_representation(data)
        data["nric"] = f"{data['nric'][0]}****{data['nric'][-4:]}"
        return data
