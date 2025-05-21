from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed


class EmailorPhoneModelBackend(ModelBackend):
    """ Custom authentication backend to allow login using usernamem, email or phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Find user by username, phone, or email
            user = UserModel.objects.get(
                Q(username__exact=username) |
                Q(primary_phone__exact=username) |
                Q(email__exact=username)
            )
        except UserModel.DoesNotExist:
            raise AuthenticationFailed("Incorrect phone number or email.")

        # Check password
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password. Please try again.")

        return user