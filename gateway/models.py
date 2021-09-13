from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, postal_code, unit_no, password=None):
        """
        Creates and saves a user with the given email and password.
        """
        if not password:
            raise ValueError("Users must have a password.")
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(
            email=self.normalize_email(email),
            postal_code=postal_code,
            unit_no=unit_no,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, postal_code, unit_no, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, postal_code, unit_no, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class SiteOwner(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    postal_code = models.CharField(max_length=6)
    unit_no = models.CharField(max_length=6)

    objects = UserManager()

    USERNAME_FIELD = "email"  # use email to recognize User
    REQUIRED_FIELDS = ["postal_code", "unit_no"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "siteowner"


class Gateway(models.Model):
    gateway_id = models.CharField(max_length=15, unique=True)
    site_owner = models.ForeignKey(SiteOwner, on_delete=models.CASCADE)
    authentication_token = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.gateway_id

    class Meta:
        db_table = "gateway"


class Identity(models.Model):
    nric = models.CharField(max_length=9, unique=True)
    fullname = models.CharField(max_length=100)
    address = models.TextField()
    phone_num = models.CharField(max_length=8, unique=True)

    class Meta:
        db_table = "identity"


class Token(models.Model):
    token_uuid = models.CharField(max_length=16)
    owner = models.ForeignKey(Identity, on_delete=models.PROTECT)
    issuer = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    hashed_pin = models.CharField(max_length=32)

    class Meta:
        db_table = "token"


class GatewayRecord(models.Model):
    token = models.ForeignKey(Token, on_delete=models.PROTECT)
    gateway = models.ForeignKey(Gateway, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gatewayrecord"
