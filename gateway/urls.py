from django.urls import path
from .views import GatewayListCreate, GatewayRecordCreate, LoginView
from knox import views as knox_views

urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("gateways/", GatewayListCreate.as_view()),
    path("gatewayrecords/", GatewayRecordCreate.as_view()),
]
