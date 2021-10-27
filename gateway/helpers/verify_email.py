import hashlib
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework.reverse import reverse
from django.conf import settings
from ..models import SiteOwner
from config.settings import SECRET_KEY


def generate_activation_key(email):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*(-_=+)"
    while True:
        saltPre = get_random_string(20, chars)
        saltPost = get_random_string(20, chars)
        activation_key = hashlib.sha512(
            (saltPre + SECRET_KEY + email + saltPost).encode("utf-8")
        ).hexdigest()
        try:
            new_session_user = SiteOwner.objects.get(activation_key=activation_key)
        except:
            break
    return activation_key


def sendVerificationEmail(request, activation_key, email):
    email_verification_error = False

    subject = "Gateway Account Verification"

    message = f"""\n
    Dear {email},

        Thank you for registering an account with us.
        Before setting up gateways for your premises, an activation key is required to verify & activate your account.

        Here is your activation key:

            {activation_key}
    """

    try:
        send_mail(subject, message, settings.SERVER_EMAIL, [email])
    except:
        email_verification_error = True
    return email_verification_error
