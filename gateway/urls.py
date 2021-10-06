from django.urls import path
from .views import GatewayRecordCreate, LoginView, GatewayAPI
from knox import views as knox_views

urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("gatewayrecords/", GatewayRecordCreate.as_view()),
    path("v1/gateways/", GatewayAPI.as_view()),
]
