from django.urls import path
from .views import (
    LoginView,
    GatewayList,
    GatewayDetail,
    GatewayRecordCreate,
    TokenDetail,
)
from knox import views as knox_views

urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("v1/gateways/", GatewayList.as_view()),
    path("v1/gateways/<int:pk>", GatewayDetail.as_view()),
    path("v1/gatewayrecord/", GatewayRecordCreate.as_view()),
    path("v1/token/<uuid:token_uuid>", TokenDetail.as_view()),
]
