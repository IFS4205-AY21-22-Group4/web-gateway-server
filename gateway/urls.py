from django.urls import path
from .views import GatewayList

urlpatterns = [
    path("gateways/", GatewayList.as_view()),
]
