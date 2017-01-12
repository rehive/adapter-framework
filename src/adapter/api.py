from logging import getLogger

from .models import Transaction

logger = getLogger('django')


class AbstractBaseInteface:
    """
    Template for Interface to handle all API calls to third-party account.
    """

    def __init__(self, account):
        # Always linked to an AdminAccount
        self.account = account

    def get_user_ref(self, user) -> dict:
        """
        Returns  third-party reference for specific user and details
        Should return dict of the form:
        {'reference': ...
         'details': {...}
         }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_user_account_id() method')

    def get_account_ref(self) -> dict:
        """
        Returns third-party operational/ admin account reference and details
        Should return dict of the form:
        {'reference': ...
         'details': {...}
         }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_details() method')

    def get_account_balance(self) -> dict:
        """
        Returns third-party account balance and details:
        Should return dict of the form
        {'balance': balance,
         'currency': 'XLM'}
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_balance() method')

    def execute(self, tx: Transaction) -> dict:
        """
        Excecutes transaction transaction with third-party and returns transaction details.
        Should return dict of the form:
        {'tx_id': 987139917439174
         'details': {...}
        }
        """
        raise NotImplementedError('subclasses of AbstractBaseUser must provide a get_account_balance() method')


class Interface(AbstractBaseInteface):
    """
    Interface implementation.
    """
    def execute(self, tx: Transaction):
        tx.status = 'Complete'

    # Implement Abstract base class methods here using the third-party's API.
