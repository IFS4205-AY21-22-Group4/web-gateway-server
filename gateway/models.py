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
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"  # use email to recognize User
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class SiteOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    postal_code = models.CharField(max_length=6)
    unit_no = models.CharField(max_length=6)

    def __str__(self):
        return self.user.email


class Gateway(models.Model):
    gateway_id = models.CharField(max_length=15, unique=True)
    site_owner = models.ForeignKey(SiteOwner, on_delete=models.CASCADE)
    authentication_token = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.gateway_id
