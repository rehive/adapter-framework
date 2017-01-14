import requests
from celery import shared_task

import logging

from django.conf import settings

from .exceptions import PlatformRequestFailedError
from .models import Transaction

logger = logging.getLogger('django')

@shared_task
def default_task():
    logger.info('running default task')
    return 'True'


@shared_task(bind=True, name='adapter.create_or_confirm_rehive_receive.task', max_retries=24, default_retry_delay=60 * 60)
def create_or_confirm_transaction(self, tx_id: int):
    tx = Transaction.objects.get(id=tx_id)

    if tx.status in ('Failed', 'Completed', 'Cancelled'):
        raise Exception('Attempting to upload failed, cancelled or already completed transaction.')

    initial_status = tx.status

    # If transaction has not yet been created, create it:
    if not tx.rehive_code:

        # URL, depending on transaction type.
        url = getattr(settings, 'REHIVE_API_URL') + 'admins/transactions/' + tx.tx_type + '/'

        # Admin authorization:
        headers = {'Authorization': 'Token ' + tx.admin_account.service_account.token}

        try:
            # Basic transaction data for api call:
            data = {
                'amount': tx.amount,
                'currency': tx.currency,
                'metadata': tx.metadata,
            }

            # Specific transaction data for api call:
            if tx.tx_type == 'withdraw':
                data.update({'from_reference': tx.from_reference})
            else:
                data.update({'recipient': tx.to_reference})

            if tx.tx_type == 'send':
                data.update({'sender': tx.from_reference})

            # Deposit now also has reference field. TODO: cleanup after APIv3
            if tx.tx_type == 'deposit':
                data.update({'from_reference': tx.from_reference})

            # Make api call:
            r = requests.post(url,
                              json=data,
                              headers=headers)

            # If successful, mark transaction as pending:
            if r.status_code in (200, 201):
                tx.rehive_response = r.json()
                tx.rehive_code = tx.rehive_response['data']['tx_code']

                if tx.tx_type not in 'Deposit':
                    tx.status = 'Pending'
                else:
                    tx.status = 'Complete'  # TODO: Currently admin deposits complete immediately
                tx.save()

            # Else mark as Failed:
            else:
                logger.info(headers)
                logger.info('Failed transaction update request: HTTP %s Error: %s' % (r.status_code, r.text))
                tx.status = 'Failed'
                tx.rehive_response = {'status': r.status_code, 'data': r.text}
                tx.save()

        # On connection error, retry:
        except (requests.exceptions.RequestException, requests.exceptions.MissingSchema) as e:
            try:
                logger.info('Retry transaction update request due to connection error.')
                self.retry(countdown=5 * 60, exc=PlatformRequestFailedError)
            except PlatformRequestFailedError:
                logger.info('Final transaction update request failure due to connection error.')

    # After creation, or if tx already exists, confirm it if necessary
    if initial_status == 'Confirmed':
        logger.info('Transaction update request.')

        # Update URL
        url = getattr(settings, 'REHIVE_API_URL') + 'admins/transactions/update/'

        # Add Authorization headers
        headers = {'Authorization': 'Token ' + tx.admin_account.service_account.token}

        try:
            # Make request
            r = requests.post(url, json={'tx_code': tx.rehive_code, 'status': 'Confirmed'}, headers=headers)

            if r.status_code in (200, 201):
                tx.rehive_response = r.json()
                tx.status = 'Complete'
                tx.save()
            else:
                logger.info(headers)
                logger.info('Failed transaction update request: HTTP %s Error: %s' % (r.status_code, r.text))
                tx.rehive_response = {'status': r.status_code, 'data': r.text}
                tx.status = 'Failed'
                tx.save()

        except (requests.exceptions.RequestException, requests.exceptions.MissingSchema) as e:
            try:
                logger.info('Retry transaction update request due to connection error.')
                self.retry(countdown=5 * 60, exc=PlatformRequestFailedError)
            except PlatformRequestFailedError:
                logger.info('Final transaction update request failure due to connection error.')
