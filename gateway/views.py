from django.contrib.auth import login
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Gateway, SiteOwner, Token, GatewayRecord
from .serializers import GatewaySerializer, GatewayRecordSerializer


class GatewayListCreate(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GatewaySerializer

    def get_queryset(self):
        """
        This method returns a list of all gateways for the current authenticated
        user.
        """
        site_owner = self.request.user
        return Gateway.objects.filter(site_owner=site_owner)

    def post(self, request, format=None):
        """
        This method adds a gateway for the current authenticated user.
        """
        site_owner = self.request.user
        num_gateways = Gateway.objects.filter(site_owner=site_owner).count()
        next_index = num_gateways + 1

        gateway_id = f"{site_owner.postal_code}-{site_owner.unit_no}-{next_index}"

        gateway = Gateway(
            gateway_id=gateway_id,
            site_owner=site_owner,
        )
        gateway.save()
        return Response("Succesfully added gateway.")


class GatewayRecordCreate(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        serializer = GatewayRecordSerializer(data=request.data)
        if serializer.is_valid():
            token_uuid = serializer.validated_data.get("token_uuid")
            token = Token.objects.get(token_uuid=token_uuid)
            gateway_id = serializer.validated_data.get("gateway_id")
            gateway = Gateway.objects.get(gateway_id=gateway_id)

            if token is None or gateway is None:
                return Response("Invalid token_uuid or gateway_id")

            if token.status != 1:
                return Response("Token inactive")

            gateway_record = GatewayRecord(
                token=token,
                gateway=gateway,
            )
            gateway_record.save()
            return Response("Added gateway record")
        return Response("TODO create gateway record")
