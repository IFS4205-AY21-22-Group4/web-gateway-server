from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import SiteOwner, Gateway, Identity, Token, MedicalRecord
import uuid
import hashlib
import binascii

User = get_user_model()


class GatewayRecordTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Add siteowner 1
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

        # Add siteowner 2
        cls.siteowner2_email = "testuser4@gmail.com"
        cls.siteowner2_password = "testpassword2"
        cls.siteowner2_postalcode = "610321"
        cls.siteowner2_unitno = "10-321"
        cls.siteowner2_auth_token = None
        cls.user2 = User.objects.create_user(
            email=cls.siteowner2_email,
            password=cls.siteowner2_password,
        )
        cls.site_owner2 = SiteOwner.objects.create(
            user=cls.user2,
            postal_code=cls.siteowner2_postalcode,
            unit_no=cls.siteowner2_unitno,
            activation_key=4321,
            email_validated=True,
        )

        # Add a gateway for siteowner1
        cls.gateway = Gateway.objects.create(
            gateway_id="610123-01-123-1",
            site_owner=cls.site_owner,
            authentication_token=None,
        )

        # Add a gateway for siteowner2
        cls.gateway2 = Gateway.objects.create(
            gateway_id="610321-10-321-1",
            site_owner=cls.site_owner2,
            authentication_token=None,
        )

        # Create valid token and vaccination status
        identity = Identity.objects.create(
            nric="S9111111A",
            fullname="Test Person",
            address="Test Address",
            phone_num="91234567",
        )

        hashed_pin = hashlib.sha256(b"123456").hexdigest()
        cls.token = Token.objects.create(
            token_uuid=str(uuid.uuid4()),
            issuer=1,
            status=True,
            hashed_pin=hashed_pin,
            owner=identity,
        )

        medical_record = MedicalRecord.objects.create(
            identity=identity,
            token=cls.token,
            vaccination_status=True,
        )

        # Create inactive token
        identity = Identity.objects.create(
            nric="S9222222A",
            fullname="Test Person 2",
            address="Test Address",
            phone_num="92234567",
        )

        hashed_pin = hashlib.sha256(b"654321").hexdigest()
        cls.inactive_token = Token.objects.create(
            token_uuid=str(uuid.uuid4()),
            issuer=1,
            status=False,
            hashed_pin=hashed_pin,
            owner=identity,
        )

        medical_record = MedicalRecord.objects.create(
            identity=identity,
            token=cls.token,
            vaccination_status=True,
        )

        # Create valid token and invalid vaccination status
        identity = Identity.objects.create(
            nric="S9323456A",
            fullname="Test Person 3",
            address="Test Address",
            phone_num="93234567",
        )

        hashed_pin = hashlib.sha256(b"123456").hexdigest()
        cls.unvax_token = Token.objects.create(
            token_uuid=str(uuid.uuid4()),
            issuer=1,
            status=True,
            hashed_pin=hashed_pin,
            owner=identity,
        )

        medical_record = MedicalRecord.objects.create(
            identity=identity,
            token=cls.token,
            vaccination_status=False,
        )

    def test_token_retrieve_partial_identity(self):
        token_url = reverse("token", kwargs={"token_uuid": self.token.token_uuid})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.get(token_url)

        self.assertEqual(response.data["token_uuid"], self.token.token_uuid)
        self.assertNotEqual(response.data["nric"], self.token.owner.nric)

    def test_gatewayrecord_invalid_token_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": str(uuid.uuid4()),
            "gateway_id": self.gateway.gateway_id,
            "pin": "123456",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Invalid token_uuid or gateway_id")

    def test_gatewayrecord_invalid_gateway_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.token.token_uuid,
            "gateway_id": "610111-01-111-9",
            "pin": "123456",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Invalid token_uuid or gateway_id")

    def test_gatewayrecord_invalid_gateway_owner_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.token.token_uuid,
            "gateway_id": self.gateway2.gateway_id,
            "pin": "123456",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Invalid gateway_id")
        pass

    def test_gatewayrecord_valid_pin_return_added(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.token.token_uuid,
            "gateway_id": self.gateway.gateway_id,
            "pin": "123456",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Added gateway record")

    def test_gatewayrecord_invalid_pin_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.token.token_uuid,
            "gateway_id": self.gateway.gateway_id,
            "pin": "654321",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Invalid PIN entered")

    def test_gatewayrecord_inactive_token_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.inactive_token.token_uuid,
            "gateway_id": self.gateway.gateway_id,
            "pin": "654321",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Token inactive")

        pass

    def test_gatewayrecord_unvaccinated_return_invalid(self):
        gatewayrecord_url = reverse("gateway_record")
        record_data = {
            "token_uuid": self.unvax_token.token_uuid,
            "gateway_id": self.gateway.gateway_id,
            "pin": "123456",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.siteowner_auth_token)
        response = self.client.post(gatewayrecord_url, record_data)

        self.assertEqual(response.data, "Person is not vaccinated")
