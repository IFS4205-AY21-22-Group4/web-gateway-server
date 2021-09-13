from django.urls import path
from .views import GatewayListCreate, GatewayRecordCreate

urlpatterns = [
    path("gateways/", GatewayListCreate.as_view()),
    path("gatewayrecord/add/", GatewayRecordCreate.as_view()),
]
