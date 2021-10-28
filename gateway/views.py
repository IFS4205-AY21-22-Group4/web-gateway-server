from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.http import Http404
from django.db.models import ProtectedError
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from .models import Gateway, MedicalRecord, SiteOwner, Token, GatewayRecord
from .serializers import (
    GatewaySerializer,
    GatewayRecordSerializer,
    TokenSerializer,
    SiteOwnerSerializer,
)
import hashlib
from .helpers import verify_email


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        site_owner = SiteOwner.objects.get(user=user)
        if not site_owner.email_validated:
            return Response("Email not verified", 401)
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class VerifyEmailView(APIView):
    """
    Verifies the email of site owner.
    """

    permission_classes = (permissions.AllowAny,)

    def get_object(self, key):
        try:
            return SiteOwner.objects.get(activation_key=key)
        except Token.DoesNotExist:
            raise Http404

    def get(self, request, key, format=None):
        site_owner = self.get_object(key)
        site_owner.email_validated = True
        site_owner.save()
        return Response("Email successfully verified")


class RegisterView(generics.CreateAPIView):
    """
    Register site owner as a user.
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = SiteOwnerSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["user"]["email"]
        activation_key = verify_email.generate_activation_key(email=email)
        email_verification_error = verify_email.sendVerificationEmail(
            request, activation_key, email
        )
        if email_verification_error:
            return Response("Unable to send email verification. Please try again")
        site_owner = serializer.save()
        site_owner.activation_key = activation_key
        site_owner.save()
        return Response(f"Account created for {site_owner.user.email}")


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
        if num_gateways == 4:
            return Response("Maximum number of gateways", 204)
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
            return Response("No gateways available to delete", 204)

        serializer = GatewaySerializer(gateway_to_delete)
        try:
            gateway_to_delete.delete()
        except ProtectedError:
            return Response("Gateways already in use for contact tracing", 405)
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
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        site_owner = SiteOwner.objects.get(user=self.request.user)
        gateways = Gateway.objects.filter(site_owner=site_owner)

        # Check gateway to update belongs to site owner
        if gateway not in gateways:
            return Response("Gateway does not belong to site owner", 403)

        # Toggle token value
        if gateway.authentication_token == None:
            # Start gateway
            # Check that current token key has not been used
            for check_gateway in gateways:
                if token_hash == check_gateway.authentication_token:
                    return Response("Token already used")
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
            token = (
                Token.objects.filter(token_uuid=token_uuid).filter(status=True).first()
            )
            gateway_id = serializer.validated_data.get("gateway_id")
            gateway = Gateway.objects.filter(gateway_id=gateway_id).first()
            pin = serializer.validated_data.get("pin")

            # Check valid token
            if token is None or gateway is None:
                return Response("Invalid token_uuid or gateway_id")

            # Check gateway belongs to authenticated site owner
            user = self.request.user
            site_owner = SiteOwner.objects.get(user=user)

            if gateway.site_owner != site_owner:
                return Response("Invalid gateway_id")

            # Check Token belongs to owner
            if not check_password(pin, token.hashed_pin):
                return Response("Invalid PIN entered")

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


class TokenDetail(APIView):
    """
    This view retrieves the partial identity of the owner associated with the
    Token.

    * Requires user to be authenticated
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, token_uuid):
        try:
            return Token.objects.get(token_uuid=token_uuid)
        except Token.DoesNotExist:
            raise Http404

    def get(self, request, token_uuid, format=None):
        token = self.get_object(token_uuid)
        serializer = TokenSerializer(token)
        return Response(serializer.data)
