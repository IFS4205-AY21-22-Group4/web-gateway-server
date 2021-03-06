from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None):
        """
        Creates and saves a user with the given email and password.
        """
        if not password:
            raise ValueError("Users must have a password.")
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"  # use email to recognize User
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        managed = True
        db_table = "user"


class SiteOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    postal_code = models.CharField(max_length=6)
    unit_no = models.CharField(max_length=6)
    activation_key = models.CharField(max_length=255, unique=True)
    email_validated = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "siteowner"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roles = models.CharField(max_length=20, blank=True)
    activation_key = models.CharField(
        max_length=255, default=1
    )  # link for email verification
    most_recent_otp = models.CharField(
        max_length=6, blank=True
    )  # value for otp verification
    email_validated = models.BooleanField(default=False)  # verify email inputted
    is_verified = models.BooleanField(default=False)  # verify otp inputted
    number_of_attempts = models.IntegerField(default=0)  # count number of attempts

    class Meta:
        db_table = "staff"


class Gateway(models.Model):
    gateway_id = models.CharField(max_length=15, unique=True)
    site_owner = models.ForeignKey(SiteOwner, on_delete=models.CASCADE)
    authentication_token = models.CharField(max_length=64, blank=False, null=True)

    def __str__(self):
        return self.gateway_id

    class Meta:
        managed = True
        db_table = "gateway"


class Identity(models.Model):
    nric = models.CharField(max_length=9, unique=True)
    fullname = models.CharField(max_length=100)
    address = models.TextField()
    phone_num = models.CharField(max_length=8, unique=True)

    class Meta:
        managed = True
        db_table = "identity"


class Token(models.Model):
    token_uuid = models.CharField(max_length=17)
    owner = models.ForeignKey(Identity, on_delete=models.PROTECT)
    issuer = models.ForeignKey(Staff, null=True, on_delete=models.SET_NULL)
    status = models.BooleanField(default=True)
    hashed_pin = models.CharField(max_length=128)

    class Meta:
        managed = True
        db_table = "token"


class MedicalRecord(models.Model):
    identity = models.OneToOneField(Identity, on_delete=models.PROTECT)
    token = models.ForeignKey(Token, on_delete=models.PROTECT, blank=True, null=True)
    vaccination_status = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "medicalrecords"


class GatewayRecord(models.Model):
    token = models.ForeignKey(Token, on_delete=models.PROTECT)
    gateway = models.ForeignKey(Gateway, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "gatewayrecord"
