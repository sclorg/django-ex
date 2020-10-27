from edivorce.apps.core.utils.derived import get_derived_data


def forms_to_file(responses_dict, initial=False):
    generated = []
    uploaded = []

    how_to_file = responses_dict.get('how_to_file')
    how_to_sign = responses_dict.get('how_to_sign')
    signing_location_both = responses_dict.get('signing_location') if how_to_sign == 'Together' else None
    signing_location_you = responses_dict.get('signing_location_you') if how_to_sign == 'Separately' else None
    signing_location_spouse = responses_dict.get('signing_location_spouse') if how_to_sign == 'Separately' else None

    derived = responses_dict.get('derived', get_derived_data(responses_dict))

    name_change_you = derived['wants_other_orders'] and responses_dict.get('name_change_you') == 'YES'
    name_change_spouse = derived['wants_other_orders'] and responses_dict.get('name_change_spouse') == 'YES'
    has_children = derived['has_children_of_marriage']

    provide_marriage_certificate = responses_dict.get('original_marriage_certificate') == 'YES'
    married_in_canada = responses_dict.get('where_were_you_married_country') == 'Canada'
    marriage_province = responses_dict.get('where_were_you_married_prov', '').strip().upper()
    married_in_quebec = married_in_canada and marriage_province.lower().startswith('q')

    if initial:
        generated.append({'doc_type': 'NJF', 'form_number': 1})
        if provide_marriage_certificate:
            uploaded.append({'doc_type': 'MC', 'party_code': 0})
            if married_in_quebec:
                uploaded.append({'doc_type': 'AFTL', 'party_code': 0})

        if signing_location_both == 'In-person' or signing_location_you == 'In-person':
            # claimant 1 is signing with a commissioner
            uploaded.append({'doc_type': 'RDP', 'party_code': 0})

        elif signing_location_you == 'Virtual' and signing_location_spouse == 'In-person':
            # claimant 1 is signing virtually and claimant 2 is not
            generated.append({'doc_type': 'RFO', 'form_number': 35})
            generated.append({'doc_type': 'RCP', 'form_number': 36})
            uploaded.append({'doc_type': 'OFI', 'party_code': 0})
            uploaded.append({'doc_type': 'EFSS', 'party_code': 1})
            uploaded.append({'doc_type': 'RDP', 'party_code': 0})
            if has_children:
                uploaded.append({'doc_type': 'AAI', 'party_code': 0})
            if name_change_you:
                uploaded.append({'doc_type': 'NCV', 'party_code': 1})

        elif signing_location_both == 'Virtual' or (signing_location_you == 'Virtual' and signing_location_spouse == 'Virtual'):
            # both parties (either together or separately) are signing virtually
            generated.append({'doc_type': 'RFO', 'form_number': 35})
            generated.append({'doc_type': 'RCP', 'form_number': 36})
            uploaded.append({'doc_type': 'OFI', 'party_code': 0})
            uploaded.append({'doc_type': 'EFSS', 'party_code': 1})
            if how_to_sign == 'Separately':
                uploaded.append({'doc_type': 'EFSS', 'party_code': 2})
            uploaded.append({'doc_type': 'RDP', 'party_code': 0})
            if has_children:
                uploaded.append({'doc_type': 'AAI', 'party_code': 0})
            if name_change_you:
                uploaded.append({'doc_type': 'NCV', 'party_code': 1})
            if name_change_spouse:
                uploaded.append({'doc_type': 'NCV', 'party_code': 2})
        else:
            return [], []

    else:  # Final Filing
        if signing_location_both == 'Virtual':
            # if both parties have signed virtually and signing together
            if has_children:
                uploaded.append({'doc_type': 'CSA', 'party_code': 0})
            uploaded.append({'doc_type': 'AFDO', 'party_code': 0})

        elif signing_location_you == 'Virtual' and signing_location_spouse == 'Virtual':
            # both parties have signed virtually and signing separately
            if has_children:
                uploaded.append({'doc_type': 'CSA', 'party_code': 1})
            uploaded.append({'doc_type': 'AFDO', 'party_code': 1})
            if has_children:
                uploaded.append({'doc_type': 'CSA', 'party_code': 2})
            uploaded.append({'doc_type': 'AFDO', 'party_code': 2})

        elif (signing_location_both == 'In-person' or signing_location_you == 'In-person' or signing_location_spouse == 'In-person') and how_to_file == 'Online':
            # at least one party has signed with a commissioner and Filing Online
            generated.append({'doc_type': 'RFO', 'form_number': 35})
            generated.append({'doc_type': 'RCP', 'form_number': 36})
            if has_children:
                uploaded.append({'doc_type': 'CSA', 'party_code': 0})
            uploaded.append({'doc_type': 'AFDO', 'party_code': 0})
            uploaded.append({'doc_type': 'OFI', 'party_code': 0})
            uploaded.append({'doc_type': 'EFSS', 'party_code': 1})
            uploaded.append({'doc_type': 'EFSS', 'party_code': 2})
            if has_children:
                uploaded.append({'doc_type': 'AAI', 'party_code': 0})
            if name_change_you:
                uploaded.append({'doc_type': 'NCV', 'party_code': 1})
            if name_change_spouse:
                uploaded.append({'doc_type': 'NCV', 'party_code': 2})
        else:
            return [], []

    return uploaded, generated
