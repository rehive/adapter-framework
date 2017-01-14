import requests
import json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from rest_framework import authentication, exceptions

from .models import User, ServiceAccount


class ExternalJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = self.get_jwt_value(request)
        url = ''.join([getattr(settings, 'REHIVE_API_URL'), 'auth/jwt/verify/'])

        try:
            r = requests.post(url, json={"token": token})

            if r.status_code == 200:
                data = json.loads(r.text)

                try:
                    ServiceAccount.objects.get(company=data['user']['company'])
                except ServiceAccount.DoesNotExist:
                    raise exceptions.AuthenticationFailed(_("Inactive service"))

                user, created = User.objects.get_or_create(identifier=data['user']['identifier'])
                user.first_name = data['user']['first_name']
                user.last_name = data['user']['last_name']
                user.email = data['user']['email']
                user.mobile_number = data['user']['mobile_number']
                user.profile = data['user']['profile']
                user.company = data['user']['company']
                user.save()

            else:
                raise exceptions.AuthenticationFailed(_('Invalid user'))

        except (requests.exceptions.RequestException, requests.exceptions.MissingSchema) as e:
            raise exceptions.AuthenticationFailed(e)

        return user, token  # authentication successful

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