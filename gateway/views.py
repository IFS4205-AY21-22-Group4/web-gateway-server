from django.contrib.auth import login
from django.http import Http404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from .models import Gateway, MedicalRecord, SiteOwner, Token, GatewayRecord
from .serializers import GatewaySerializer, GatewayRecordSerializer
from cryptography.hazmat.primitives import hashes
import binascii


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        print("login passed")
        return super(LoginView, self).post(request, format=None)


class GatewayList(APIView):
    """
    List all gateways, or create/delete gateway from the back.

    * Requires user to be authenticated
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        This method returns a list of all gateways for the current authenticated
        user.
        """
        site_owner = SiteOwner.objects.get(user=self.request.user)
        gateways = Gateway.objects.filter(site_owner=site_owner)
        serializer = GatewaySerializer(gateways, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        This method adds a gateway from the back for the current authenticated user.
        """
        site_owner = SiteOwner.objects.get(user=self.request.user)
        num_gateways = Gateway.objects.filter(site_owner=site_owner).count()
        next_index = num_gateways + 1

        gateway_id = f"{site_owner.postal_code}-{site_owner.unit_no}-{next_index}"

        gateway = Gateway(
            gateway_id=gateway_id,
            site_owner=site_owner,
        )
        gateway.save()

        serializer = GatewaySerializer(gateway)
        return Response(serializer.data)

    def delete(self, request, format=None):
        """
        This method removes a gateway from the back for the current authenticated user.
        """
        site_owner = SiteOwner.objects.get(user=self.request.user)
        gateway_to_delete = (
            Gateway.objects.filter(site_owner=site_owner).order_by("gateway_id").last()
        )
        if gateway_to_delete is None:
            return Response("No gateways available to delete", 404)

        serializer = GatewaySerializer(gateway_to_delete)
        gateway_to_delete.delete()
        return Response(serializer.data)


class GatewayDetail(APIView):
    """
    Updates  authentication token of specified gateway.

    * Requires user to be authenticated
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Gateway.objects.get(id=pk)
        except Gateway.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        """
        This method updates the authentication token of the gateway.
        """
        gateway = self.get_object(pk)

        # Get token value
        auth = self.request.headers["Authorization"].split()
        if auth[0].lower() != "token":
            return Response(404)
        if len(auth) == 1:
            return Response(404)
        elif len(auth) > 2:
            return Response(404)
        token = auth[1]
        digest = hashes.Hash(hashes.SHA256())
        digest.update(binascii.unhexlify(token))
        token_hash = binascii.hexlify(digest.finalize()).decode()

        site_owner = SiteOwner.objects.get(user=self.request.user)
        gateways = Gateway.objects.filter(site_owner=site_owner)

        # Toggle token value
        if gateway.authentication_token == None:
            # Start gateway
            # Check that current token key has not been used
            for check_gateway in gateways:
                if token_hash == check_gateway.authentication_token:
                    return Response("Token already used", 403)
            gateway.authentication_token = token_hash
        else:
            # Stop gateway
            gateway.authentication_token = None
        gateway.save()

        serializer = GatewaySerializer(gateway)
        return Response(serializer.data)


class GatewayRecordCreate(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        serializer = GatewayRecordSerializer(data=request.data)
        if serializer.is_valid():
            token_uuid = serializer.validated_data.get("token_uuid")
            token = Token.objects.filter(token_uuid=token_uuid).first()
            gateway_id = serializer.validated_data.get("gateway_id")
            gateway = Gateway.objects.filter(gateway_id=gateway_id).first()

            # Check valid token
            if token is None or gateway is None:
                return Response("Invalid token_uuid or gateway_id")

            # Check gateway belongs to authenticated site owner
            user = self.request.user
            site_owner = SiteOwner.objects.get(user=user)

            if gateway.site_owner != site_owner:
                return Response("Invalid gateway_id")

            # Check active token
            if token.status != 1:
                return Response("Token inactive")

            # Get vaccination status
            medical_record = MedicalRecord.objects.get(identity=token.owner)
            if medical_record.vaccination_status != True:
                return Response("Person is not vaccinated")

            gateway_record = GatewayRecord(
                token=token,
                gateway=gateway,
            )
            gateway_record.save()
            return Response("Added gateway record")
        return Response("Invalid")
