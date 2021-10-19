from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    GatewayList,
    GatewayDetail,
    GatewayRecordCreate,
    TokenDetail,
)
from knox import views as knox_views

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path("v1/gateways/", GatewayList.as_view(), name="gateways"),
    path("v1/gateways/<int:pk>", GatewayDetail.as_view(), name="gateways_detail"),
    path("v1/gatewayrecord/", GatewayRecordCreate.as_view(), name="gateway_record"),
    path("v1/token/<str:token_uuid>", TokenDetail.as_view(), name="token"),
]
