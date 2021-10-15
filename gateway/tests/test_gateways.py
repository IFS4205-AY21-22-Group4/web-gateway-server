from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import SiteOwner, Gateway

User = get_user_model()


class GatewayTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        )
        login_url = reverse("login")
        login_data = {
            "username": cls.siteowner_email,
            "password": cls.siteowner_password,
        }
        cls.client = APIClient()
        response = cls.client.post(login_url, login_data)
        cls.siteowner_auth_token = response.data["token"]

    def test_siteowner_add_gateway(self):
        total_gateways_before = Gateway.objects.filter(
            site_owner=self.site_owner
        ).count()

        # Add gateway
        gateway_url = reverse("gateways")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gateway_url)

        total_gateways_after = Gateway.objects.filter(
            site_owner=self.site_owner
        ).count()

        self.assertEqual(total_gateways_before + 1, total_gateways_after)

        # Check gateway id added is correct
        gateways = Gateway.objects.filter(site_owner=self.site_owner)
        for idx, gateway in enumerate(gateways, start=1):
            self.assertEqual(
                gateway.gateway_id,
                f"{self.site_owner.postal_code}-{self.site_owner.unit_no}-{idx}",
            )

    def test_siteowner_add_gateways_limit(self):
        pass

    def test_siteowner_can_remove_gateway_without_records(self):
        pass

    def test_siteowner_cannot_remove_gateway_with_records(self):
        pass
