from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import SiteOwner

User = get_user_model()


class SiteOwnerLoginTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.siteowner_email = "testuser1@gmail.com"
        cls.siteowner_password = "testpassword1"
        cls.siteowner_postalcode = "610123"
        cls.siteowner_unitno = "01-123"
        cls.siteowner_auth_token = None
        cls.user = User.objects.create_user(
            email=cls.siteowner_email,
            password=cls.siteowner_password,
        )
        cls.site_owner = SiteOwner.objects.create(
            user=cls.user,
            postal_code=cls.siteowner_postalcode,
            unit_no=cls.siteowner_unitno,
            activation_key=1234,
            email_validated=True,
        )

    def test_valid_login_returns_valid_auth_token(self):
        login_url = reverse("login")
        login_data = {
            "username": self.siteowner_email,
            "password": self.siteowner_password,
        }
        response = self.client.post(login_url, login_data)
        self.siteowner_auth_token = response.data["token"]

        # Check returns token
        self.assertTrue(self.siteowner_auth_token)

        url = reverse("gateways")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.get(url)
        # Check valid auth token
        self.assertEqual(response.status_code, 200)

    def test_invalid_login_returns_400(self):
        login_url = reverse("login")
        login_data = {
            "username": self.siteowner_email,
            "password": "somebadpassword",
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 400)

    def test_logout_deletes_auth_token(self):
        login_url = reverse("login")
        login_data = {
            "username": self.siteowner_email,
            "password": self.siteowner_password,
        }
        response = self.client.post(login_url, login_data)
        self.siteowner_auth_token = response.data["token"]

        # Check succesful log out
        logout_url = reverse("logout")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 204)

        # Check unable to reuse token
        gateway_url = reverse("gateways")
        response = self.client.get(gateway_url)
        self.assertNotEqual(response.status_code, 200)
