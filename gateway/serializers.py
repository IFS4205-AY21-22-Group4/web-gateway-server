from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from .models import Gateway, GatewayRecord, Token, SiteOwner
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = ("id", "gateway_id", "authentication_token")


class GatewayRecordSerializer(serializers.Serializer):
    token_uuid = serializers.CharField(max_length=36)
    gateway_id = serializers.CharField(max_length=15)
    pin = serializers.CharField(max_length=6)


class TokenSerializer(serializers.ModelSerializer):
    nric = serializers.ReadOnlyField(source="owner.nric")

    class Meta:
        model = Token
        fields = ("token_uuid", "nric")

    def to_representation(self, data):
        data = super(TokenSerializer, self).to_representation(data)
        data["nric"] = f"{data['nric'][0]}****{data['nric'][-4:]}"
        return data


class SiteOwnerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Email already in use."
            )
        ],
    )
    postal_code = serializers.IntegerField()
    unit_no = serializers.CharField(max_length=10)
    password = serializers.CharField(
        source="user.password", write_only=True, validators=[validate_password]
    )
    password2 = serializers.CharField(source="user.password2", write_only=True)

    def validate(self, data):
        if data["user"]["password"] != data["user"]["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields don't match"}
            )

        return data

    def create(self, validated_data):
        # Create user
        user = User.objects.create_user(
            email=validated_data["user"]["email"],
            password=validated_data["user"]["password"],
        )

        # Create siteowner
        siteowner = SiteOwner.objects.create(
            user=user,
            postal_code=validated_data["postal_code"],
            unit_no=validated_data["unit_no"],
        )

        return siteowner

    class Meta:
        model = SiteOwner
        validators = [
            UniqueTogetherValidator(
                queryset=SiteOwner.objects.all(),
                fields=("postal_code", "unit_no"),
                message="There is already an account for this site",
            )
        ]
        fields = ("email", "password", "password2", "postal_code", "unit_no")
