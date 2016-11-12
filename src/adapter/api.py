from logging import getLogger

from .models import SendTransaction, UserAccount
from celery import shared_task

logger = getLogger('django')


class AbstractBaseInteface:
    """
    Template for Interface to handle all API calls to third-party account.
    """

    def __init__(self, account):
        # Always linked to an AdminAccount
        self.account = account

    def get_user_account_id(self):
        """
        Generated or retrieve an account ID from third-party API or cryptocurrency.
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_user_account_id() method')

    def get_user_account_details(self) -> dict:
        """
        Returns account id and details
        Should return dict of the form:
        {'account_id': ...
         'details': {...}
         }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_user_account_details() method')

    def get_account_id(self):
        """
        Generated or retrieve an account ID from third-party API or cryptocurrency.
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_id() method')

    def get_account_details(self) -> dict:
        """
        Returns account id and details
        Should return dict of the form:
        {'account_id': ...
         'details': {...}
         }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_details() method')

    def get_account_balance(self) -> dict:
        """
        Returns account balance and details:
        Should return dict of the form
        {'balance': balance,
         'details': {'divisibility': 7,
                     'currency': 'XLM'}
        }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_balance() method')

    def send(self, tx: SendTransaction) -> dict:
        """
        Sends transaction from account and return transaction details.
        Should return dict of the form:
        {'tx_id': 987139917439174
         'details': {...}
        }
        """


class Interface(AbstractBaseInteface):
    """
    Interface implementation.
    """
    pass


class AbstractReceiveWebhookInterfaceBase:
    """
    If an external webhook service is used to create receive transactions,
    these can be subscribed to using this interface.
    """
    def __init__(self, account):
        # Always linked to an AdminAccount
        self.account = account

    def subscribe_to_all(self):
        raise NotImplementedError()

    def unsubscribe_from_all(self):
        raise NotImplementedError()


class WebhookReceiveInterface(AbstractReceiveWebhookInterfaceBase):
    """
    Webhook implementation
    """


@shared_task()
def process_webhook_receive(webhook_type, receive_id, data):
    user_account = UserAccount.objects.get(id=receive_id)
    # TODO: add webhook logic for creating and confirming transactions here.
