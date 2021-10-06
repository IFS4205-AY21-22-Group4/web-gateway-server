from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Gateway, SiteOwner

User = get_user_model()


class SiteOwnerTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="testuser1@gmail.com",
            password="testpassword1",
        )
        site_owner = SiteOwner.objects.create(
            user=user,
            postal_code="610123",
            unit_no="123",
        )

    def test_siteowner_exists(self):
        user = User.objects.get(email="testuser1@gmail.com")
        site_owner = SiteOwner.objects.get(user=user)
        self.assertEqual(site_owner.user.email, "testuser1@gmail.com")
        self.assertNotEqual(site_owner.user.password, "testpassword1")


class GatewayTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="testuser1@gmail.com",
            password="testpassword1",
        )
        site_owner = SiteOwner.objects.create(
            user=user,
            postal_code="610123",
            unit_no="123",
        )

        for i in range(1, 5 + 1):
            Gateway.objects.create(
                gateway_id=f"{site_owner.postal_code}-{site_owner.unit_no}-{i}",
                site_owner=site_owner,
            )

    def test_siteowner_add_gateways(self):
        user = User.objects.get(email="testuser1@gmail.com")
        site_owner = SiteOwner.objects.get(user=user)
        gateway_total = Gateway.objects.filter(site_owner=site_owner).count()
        gateways = Gateway.objects.filter(site_owner=site_owner)
        self.assertEqual(gateway_total, 5)
        for idx, gateway in enumerate(gateways, start=1):
            self.assertEqual(
                gateway.gateway_id,
                f"{site_owner.postal_code}-{site_owner.unit_no}-{idx}",
            )
