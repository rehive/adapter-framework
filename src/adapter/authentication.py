import requests
import json

from django.utils.encoding import smart_text
from rest_framework import authentication, exceptions

from src.config import settings
from .models import User


class AuthUser:
    details = User()
    is_authenticated = False,
    token = None

    def __str__(self):
        return str(self.details)

    def __init__(self, details=None, authenticated=False, token=None):
        self.details = details
        self.is_authenticated = authenticated,
        self.token = token


class ExternalJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = self.get_jwt_value(request)
        url = ''.join([getattr(settings, 'REHIVE_API_URL'), 'auth/jwt/verify/'])

        try:
            r = requests.post(url, json={"token": token})

            # print(r.text)

            if r.status_code == 200:
                data = json.loads(r.text)

                user, created = User.objects.get_or_create(identifier=data['user']['identifier'])
                user.first_name = data['user']['first_name']
                user.last_name = data['user']['last_name']
                user.email = data['user']['email']
                user.mobile_number = data['user']['mobile_number']
                user.profile = data['user']['profile']
                user.save()

                adapter_user = AuthUser(details=user,
                                        authenticated=True,
                                        token=token)
            else:
                raise exceptions.AuthenticationFailed('Invalid user')

        except (requests.exceptions.RequestException, requests.exceptions.MissingSchema) as e:
            raise exceptions.AuthenticationFailed(e)

        return (adapter_user, None)  # authentication successful

    @staticmethod
    def get_jwt_value(request):
        try:
            auth = request.META['HTTP_AUTHORIZATION'].split()
        except KeyError:
            return None

        if not auth or smart_text(auth[0].lower()) != "jwt":
            return None

        if not auth[1]:
            return None

        return auth[1]


# Check that the required secret key matches the secret sent in the authorization headers
def authenticate_admin(required_secret, request, view):
    secret = request.META.get('HTTP_AUTHORIZATION')
    if (not secret) or not (('Secret ' + required_secret) == secret):
       return False

    return True