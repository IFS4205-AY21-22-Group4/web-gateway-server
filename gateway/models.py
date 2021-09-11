from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None):
        """
        Creates and saves a user with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email addres")

        site_owner = self.model(
            email=self.normalize_email(email),
        )

        site_owner.set_password(password)
        site_owner.is_staff = True
        site_owner.save(using=self._db)
        return site_owner

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        site_owner = self.create_user(email, password=password)
        site_owner.is_superuser = True
        site_owner.save(using=self._db)
        return site_owner


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"  # use email to recognize User
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class SiteOwner(User):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    postal_code = models.CharField(max_length=6)
    unit_no = models.CharField(max_length=6)


class Gateway(models.Model):
    gateway_id = models.CharField(max_length=15, unique=True)
    site_owner = models.ForeignKey(SiteOwner, on_delete=models.CASCADE)
    authentication_token = models.CharField(max_length=40)

    def __str__(self):
        return self.gateway_id


class Identity(models.Model):
    nric = models.CharField(max_length=9, unique=True)
    fullname = models.CharField(max_length=100)
    address = models.TextField()
    phone_num = models.CharField(max_length=8)


class Token(models.Model):
    token_uuid = models.CharField(max_length=16, unique=True)
    owner = models.ForeignKey(Identity, on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    hashed_pin = models.CharField(max_length=32)


class GatewayRecord(models.Model):
    gateway_id = models.ForeignKey(Gateway, on_delete=models.CASCADE)
    token_uuid = models.ForeignKey(Token, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
