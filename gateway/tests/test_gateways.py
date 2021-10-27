from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import SiteOwner, Gateway, Identity, Token, GatewayRecord
import binascii
import uuid
import random
import hashlib

User = get_user_model()


class GatewayTestCase(APITestCase):
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
        gateway_url = reverse("gateways")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        for i in range(5):
            response = self.client.post(gateway_url)

        self.assertTrue(response.data, "Maximum number of gateways")

    def test_siteowner_can_remove_gateway_without_records(self):
        gateway_url = reverse("gateways")
        total_gateways_before = Gateway.objects.filter(
            site_owner=self.site_owner
        ).count()

        # Add gateway
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gateway_url)

        # Remove gateway
        response = self.client.delete(gateway_url)

        total_gateways_after = Gateway.objects.filter(
            site_owner=self.site_owner
        ).count()

        self.assertTrue(response.status_code, 200)
        self.assertEqual(total_gateways_before, total_gateways_after)

    def test_siteowner_cannot_remove_gateway_with_records(self):
        gateway_url = reverse("gateways")
        total_gateways_before = Gateway.objects.filter(
            site_owner=self.site_owner
        ).count()

        # Add gateway
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gateway_url)
        gateway = Gateway.objects.get(gateway_id=response.data["gateway_id"])

        # Create token
        identity = Identity.objects.create(
            nric="S9123456A",
            fullname="Test Person",
            address="Test Address",
            phone_num="91234567",
        )
        token = Token.objects.create(
            token_uuid=str(uuid.uuid4()),
            issuer=1,
            status=1,
            hashed_pin=hex(random.getrandbits(256))[2:],
            owner=identity,
        )

        # Add gateway record related to gateway
        GatewayRecord.objects.create(gateway=gateway, token=token)

        # Delete gateway
        response = self.client.delete(gateway_url)

        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.data, "Gateways already in use for contact tracing")

    def test_siteowner_cannot_remove_empty_gateways(self):
        gateway_url = reverse("gateways")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.delete(gateway_url)

        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.data, "No gateways available to delete")

    def test_siteowner_with_auth_token_can_toggle_gateway_auth_token(self):
        # Add gateway
        gateway_url = reverse("gateways")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gateway_url)

        gateway = Gateway.objects.get(gateway_id=response.data["gateway_id"])

        # Add auth_token
        gateway_url = reverse("gateways_detail", kwargs={"pk": gateway.id})
        response = self.client.put(gateway_url)

        token_hash = hashlib.sha256(self.siteowner_auth_token.encode()).hexdigest()

        self.assertEqual(response.data["authentication_token"], token_hash)

        # Remove auth_token
        gateway_url = reverse("gateways_detail", kwargs={"pk": gateway.id})
        response = self.client.put(gateway_url)

        self.assertEqual(response.data["authentication_token"], None)
