from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import User


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get("access_token")
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")
