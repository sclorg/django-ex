from edivorce.apps.core.models import UserResponse


def file_documents(user, initial=False):
    """ Save dummy data for now. Eventually replace with data from CSO. """
    prefix = 'initial' if initial else 'final'
    _save_response(user, f'{prefix}_filing_submitted', True)

    package_number = '123-456-789'
    _save_response(user, f'{prefix}_filing_package_number', package_number)

    receipt_link = 'https://justice.gov.bc.ca/cso/payment/viewReceipt.do'
    _save_response(user, f'{prefix}_filing_receipt_link', receipt_link)

    package_link = 'https://justice.gov.bc.ca/cso/register.do'
    _save_response(user, f'{prefix}_filing_package_link', package_link)


def _save_response(user, question, value):
    response, _ = UserResponse.objects.get_or_create(bceid_user=user, question_id=question)
    response.value = value
    response.save()
