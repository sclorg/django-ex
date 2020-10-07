import random

from django.conf import settings

from edivorce.apps.core.models import UserResponse


def file_documents(user, initial=False):
    """ Save dummy data for now. Eventually replace with data from CSO. """
    prefix = 'initial' if initial else 'final'
    _save_response(user, f'{prefix}_filing_submitted', True)

    package_number_parts = []
    for _ in range(3):
        num = ''
        for _ in range(3):
            num += str(random.randint(0, 9))
        package_number_parts.append(num)

    package_number = '-'.join(package_number_parts)
    _save_response(user, f'{prefix}_filing_package_number', package_number)

    if settings.DEPLOYMENT_TYPE == 'localdev':
        base_url = 'https://dev.justice.gov.bc.ca'
    else:
        base_url = settings.PROXY_BASE_URL

    receipt_link = base_url + '/cso/payment/viewReceipt.do?packageNumber=' + package_number
    _save_response(user, f'{prefix}_filing_receipt_link', receipt_link)

    package_link = base_url + '/cso/register.do?packageNumber=' + package_number
    _save_response(user, f'{prefix}_filing_package_link', package_link)


def _save_response(user, question, value):
    response, _ = UserResponse.objects.get_or_create(bceid_user=user, question_id=question)
    response.value = value
    response.save()
