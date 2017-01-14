from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .authentication import ExternalJWTAuthentication
from .permissions import UserPermission, AdminPermission
from .api import Interface
from .models import AdminAccount, Transaction
from logging import getLogger

from .throttling import NoThrottling

from .serializers import TransactionSerializer

logger = getLogger('django')


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def adapter_root(request, format=None):
    """
    ### Notes:

    To make use of this adapter:

    1) Set the Rehive webhooks for each tx type to match their corresponding endpoints below.

    2) Set a secret key for each transaction webhook

    3) Ensure the the required ENV variables have been added to the server.

    **Required ENV variables:**

    In order to use the  adapter you must set the following ENV variables on the server.

    `REHIVE_API_TOKEN` : Secret Key for authenticating with Rehive for admin functions.

    `REHIVE_API_URL` : Rehive API URL

    `ADAPTER_SECRET_KEY`: Secret Key for adapter endpoints.

    ---

    """

    return Response({'Withdraw': reverse('adapter-api:withdraw',
                                         request=request,
                                         format=format),
                     'Deposit': reverse('adapter-api:deposit',
                                        request=request,
                                        format=format),
                     })


class WithdrawView(GenericAPIView):
    allowed_methods = ('POST',)
    throttle_classes = (NoThrottling,)
    serializer_class = TransactionSerializer
    authentication_classes = (ExternalJWTAuthentication,)
    permission_classes = (UserPermission,)

    def post(self, request, *args, **kwargs):
        # Get user model from auth user object:
        user = request.user

        tx = Transaction.objects.create_withdraw(user=user,
                                                 amount=request.data.get('amount'),
                                                 currency=request.data.get('currency', ''),
                                                 to_reference=request.data.get('to_reference'),
                                                 note=request.data.get('note'),
                                                 metadata=request.data.get('metadata', {}))

        # Execute transaction using third-party API and upload to Rehive:
        tx.execute()
        tx.upload_to_rehive()
        tx.refresh_from_db()

        return Response({'status': 'success',
                         'data': {'tx_code': tx.rehive_code}})

    def get(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('GET')


class DepositView(GenericAPIView):
    allowed_methods = ('POST',)
    throttle_classes = (NoThrottling,)
    serializer_class = TransactionSerializer
    authentication_classes = (ExternalJWTAuthentication,)
    permission_classes = (UserPermission,)

    def post(self, request, *args, **kwargs):
        # Get user model from authentication backend:
        user = request.user

        tx = Transaction.objects.create_deposit(user=user,
                                                amount=request.data.get('amount'),
                                                currency=request.data.get('currency'),
                                                from_reference=request.data.get('from_reference'),
                                                note=request.data.get('note'),
                                                metadata=request.data.get('metadata', {}))

        # Execute transaction using third-party API and upload to Rehive:
        tx.execute()
        tx.upload_to_rehive()
        tx.refresh_from_db()

        return Response({'status': 'success',
                         'data': {'tx_code': tx.rehive_code}})

    def get(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('GET')


class OperatingAccountView(APIView):
    allowed_methods = ('GET',)
    throttle_classes = (NoThrottling,)
    authentication_classes = ()
    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('POST')

    def get(self, request, *args, **kwargs):
        account = AdminAccount.objects.get(default=True)
        interface = Interface(account=account)
        details = interface.get_account_ref()
        return Response(details)
