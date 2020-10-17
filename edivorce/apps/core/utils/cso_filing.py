import random

from django.conf import settings

from edivorce.apps.core.models import UserResponse
from edivorce.apps.core.utils.derived import get_derived_data


def file_documents(user, initial=False):
    """ Save dummy data for now. Eventually replace with data from CSO. """
    prefix = 'initial' if initial else 'final'
    _save_response(user, f'{prefix}_filing_submitted', True)

    if not initial:
        _save_response(user, f'final_filing_status', 'Submitted')

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


def forms_to_file(responses_dict, initial=False):
    forms = []
    derived = responses_dict.get('derived', get_derived_data(responses_dict))
    if initial:
        forms.append({'doc_type': 'MC', 'party_code': 0})

        how_to_sign = responses_dict.get('how_to_sign')
        signing_location_both = responses_dict.get('signing_location') if how_to_sign == 'Together' else None
        signing_location_you = responses_dict.get('signing_location_you') if how_to_sign == 'Separately' else None
        signing_location_spouse = responses_dict.get('signing_location_spouse') if how_to_sign == 'Separately' else None

        if signing_location_both == 'In-person' or signing_location_you == 'In-person':
            forms.append({'doc_type': 'AFTL', 'party_code': 0})
            forms.append({'doc_type': 'RDP', 'party_code': 0})
        elif signing_location_you == 'Virtual' and signing_location_spouse == 'In-person':
            forms.append({'doc_type': 'AFTL', 'party_code': 0})
            forms.append({'doc_type': 'OFI', 'party_code': 0})
            forms.append({'doc_type': 'EFSS', 'party_code': 1})
            forms.append({'doc_type': 'RDP', 'party_code': 0})
            if derived['has_children_of_marriage']:
                forms.append({'doc_type': 'AAI', 'party_code': 0})
            if derived['wants_other_orders'] and responses_dict.get('name_change_you') == 'YES':
                forms.append({'doc_type': 'NCV', 'party_code': 1})
        elif signing_location_both == 'Virtual' or (signing_location_you == 'Virtual' and signing_location_spouse == 'Virtual'):
            forms.append({'doc_type': 'AFTL', 'party_code': 0})
            forms.append({'doc_type': 'OFI', 'party_code': 0})
            forms.append({'doc_type': 'EFSS', 'party_code': 1})
            forms.append({'doc_type': 'EFSS', 'party_code': 2})
            forms.append({'doc_type': 'RDP', 'party_code': 0})
            if derived['has_children_of_marriage']:
                forms.append({'doc_type': 'AAI', 'party_code': 0})
            if derived['wants_other_orders'] and responses_dict.get('name_change_you') == 'YES':
                forms.append({'doc_type': 'NCV', 'party_code': 1})
            if derived['wants_other_orders'] and responses_dict.get('name_change_spouse') == 'YES':
                forms.append({'doc_type': 'NCV', 'party_code': 2})
        else:
            return []
    return forms
