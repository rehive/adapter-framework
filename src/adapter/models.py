from logging import getLogger

import datetime
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.timezone import utc

from .api import Interface

logger = getLogger('django')


class User(models.Model):
    """
    Model for storing info linking to a Rehive User.
    """
    identifier = models.CharField(max_length=200, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, )
    mobile_number = models.CharField(max_length=24, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    def __str__(self):
        return str(self.identifier)

    def save(self, *args, **kwargs):
        if not self.id:  # On create
            self.created = datetime.datetime.now(tz=utc)

        self.updated = datetime.datetime.now(tz=utc)
        return super(User, self).save(*args, **kwargs)


class TransactionManager(models.Manager):
    """
    Manager functions for creating transactions.
    """
    def create_deposit(self, user, amount, fee, currency, note, metadata, account_name=None):

        if account_name == 'None':
            account = AdminAccount.objects.get(type='deposit', default='True')
        else:
            account = AdminAccount.objects.get(name=account_name)  # for multiple account scenarios.

        tx = self.create(tx_type='deposit',
                         user=user,
                         to_reference=user.identifier,
                         amount=amount,
                         fee=fee,
                         currency=currency,
                         note=note,
                         admin_account=account,
                         metadata=metadata)

        return tx

    def create_withdraw(self, user, amount, fee, currency, note, metadata, account_name=None):

        if account_name == 'None':
            account = AdminAccount.objects.get(type='deposit', default='True')
        else:
            account = AdminAccount.objects.get(name=account_name)  # for multiple account scenarios.

        tx = self.create(tx_type='withdraw',
                         user=user,
                         amount=amount,
                         fee=fee,
                         currency=currency,
                         note=note,
                         admin_account=account,
                         metadata=metadata)

        return tx


class Transaction(models.Model):
    """
    Third-party transaction model. Includes methods for creating/ confirming on  Rehive and for executing with the
    third-party.
    """
    STATUS = (
        ('Waiting', 'Waiting'),
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),  # Confirmed but not yet uploaded to rehive
        ('Complete', 'Complete'),  # Confirmed and uploaded to rehive
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey('adapter.User', null=True, blank=True)
    rehive_code = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    external_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    tx_type = models.CharField(max_length=50, choices=TYPE, null=False, blank=False)
    to_reference = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    from_reference = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    amount = models.BigIntegerField(default=0)
    fee = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=12, null=False, blank=False)
    status = models.CharField(max_length=24, choices=STATUS, null=True, blank=True)
    note = models.TextField(max_length=100, null=True, blank=True, default='')
    metadata = JSONField(null=True, blank=True, default={})
    rehive_response = JSONField(null=True, blank=True, default={})
    admin_account = models.ForeignKey('adapter.AdminAccount')
    created = models.DateTimeField()
    updated = models.DateTimeField()
    completed = models.DateTimeField(null=True, blank=True)

    objects = TransactionManager()

    def save(self, *args, **kwargs):
        if not self.id:  # On create
            self.created = datetime.datetime.now(tz=utc)

        self.updated = datetime.datetime.now(tz=utc)
        return super(Transaction, self).save(*args, **kwargs)

    def upload_to_rehive(self):
        from .rehive_tasks import create_or_confirm_transaction
        self.refresh_from_db()
        create_or_confirm_transaction(self.id)

    def execute(selfs):
        interface = Interface(account=self.admin_account)
        pass

    def cancel(self):
        self.status = 'Cancelled'
        self.completed = datetime.datetime.now(tz=utc)
        self.save()


# HotWallet/ Operational Accounts for sending or receiving on behalf of users.
# Admin accounts usually have a secret key to authenticate with third-party provider (or XPUB for key generation).
class AdminAccount(models.Model):
    """Operational Account with third party for depositing/ withdrawing on behalf of users."""

    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)  # e.g. deposit or withdraw
    secret = JSONField(null=True, blank=True, default={})  # crypto seed, private key or XPUB
    metadata = JSONField(null=True, blank=True, default={})
    default = models.BooleanField(default=False)

    def execute(self, tx: Transaction) -> bool:
        """Execute transaction with third-party and update Rehive."""
        from .rehive_tasks import create_or_confirm_transaction
        """
        Initiates a send transaction using the Admin account.
        """
        interface = Interface(account=self)
        interface.execute(tx)  # Execute transaction with third-party
        create_or_confirm_transaction(tx_id=tx.id)  # upload the transaction to rehive
        return True

    # Return account id (e.g. Bitcoin address)
    def get_account_ref(self) -> str:
        """
        Returns third party identifier of Admin account. E.g. Bitcoin address.
        """
        interface = Interface(account=self)
        return interface.get_account_id()

    def get_user_ref(self, user: User) -> str:
        """
        Returns reference for a specific user (e.g. bitcoin receive address).
        :param user:
        :return:
        """
        interface = Interface(account=self)
        return interface.get_user_ref(user=user)

    def get_account_balance(self) -> int:
        interface = Interface(account=self)
        return interface.get_account_balance()
