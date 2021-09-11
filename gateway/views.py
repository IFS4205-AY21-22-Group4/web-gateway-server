from rest_framework import generics
from .models import Gateway
from .serializers import GatewaySerializer


class GatewayList(generics.ListCreateAPIView):
    serializer_class = GatewaySerializer

    def get_queryset(self):
        """
        This view should only return a list of all gateways for the currently
        authenticated user.
        """
        user = self.request.user
        return Gateway.objects.filter(site_owner=user)
