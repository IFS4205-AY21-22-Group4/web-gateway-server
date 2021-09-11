from django.contrib.auth import login
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from .models import Gateway, SiteOwner
from .serializers import GatewaySerializer


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class GatewayList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = GatewaySerializer

    def get_queryset(self):
        """
        This view should only return a list of all gateways for the currently
        authenticated user.
        """
        user = self.request.user
        site_owner = SiteOwner.objects.get(user=user)
        return Gateway.objects.filter(site_owner=site_owner)

    def post(self, request, format=None):
        user = self.request.user
        site_owner = SiteOwner.objects.get(user=user)
        num_gateways = Gateway.objects.filter(site_owner=site_owner).count()
        next_index = num_gateways + 1

        gateway_id = f"{site_owner.postal_code}-{site_owner.unit_no}-{next_index}"

        gateway = Gateway(
            gateway_id=gateway_id,
            site_owner=site_owner,
        )
        gateway.save()
        return Response("Succesfully added gateway.")
