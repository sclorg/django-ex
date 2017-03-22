from django import template
import json

register = template.Library()


@register.simple_tag
def reformat_value(source, question_key):
    """
    Reformat user response on summary page
    ie) Remove [], make it a bullet point form
    """
    try:
        lst = json.loads(source)
        if len(lst) == 1:
            return lst[0]
        else:
            return process_list(lst, question_key)
    except:
        if question_key == 'spouse_support_details' or question_key == 'other_orders_detail'\
                or question_key == 'provide_certificate_later_reason' or question_key == 'not_provide_certificate_reason':
            text_list = source.split('\n')
            tag = ["<ul>"]
            for value in text_list:
                tag.append('<li>' + value + '</li>')
            tag.append('</ul>')
            return ''.join(tag)
        return source


def process_list(lst, question_key):
    tag = ["<ul>"]
    if question_key.startswith('other_name_'):
        for alias_type, value in lst:
            if value != '':
                tag.append('<li>' + alias_type + ' ' + value + '</li>')
    else:
        for value in lst:
            tag.append('<li>' + value + '</li>')
    tag.append('</ul>')
    return ''.join(tag)


@register.simple_tag
def combine_address(source):
    """
        Reformat address to combine them into one cell with multiple line
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '<td width="25%">'
    end_tag = '</td></tr>'

    address_you = ""
    fax_you = ""
    email_you = ""
    address_spouse = ""
    fax_spouse = ""
    email_spouse = ""
    is_specific_date = False
    effective_date = ""

    for item in source:
        q_id = item['question_id']
        if "you" in q_id:
            if "email" not in q_id and "fax" not in q_id:
                if q_id == "address_to_send_official_document_country_you":
                    continue
                address_you += item["value"] + '<br />'
            elif "fax" in q_id:
                fax_you = item["value"]
            elif "email" in q_id:
                email_you = item["value"]
        elif "spouse" in q_id:
            if "email" not in q_id and "fax" not in q_id:
                if q_id == "address_to_send_official_document_country_spouse":
                    continue
                address_spouse += item["value"] + '<br />'
            elif "fax" in q_id:
                fax_spouse = item["value"]
            elif "email" in q_id:
                email_spouse = item["value"]
        elif q_id == "divorce_take_effect_on":
            if item['value'] == "specific date":
                is_specific_date = True
            else:
                effective_date = item['value']
        elif q_id == "divorce_take_effect_on_specific_date" and is_specific_date:
            effective_date = item['value']

    if address_you != "":
        tags.append(first_column + "What is the best address to send you official court documents?</td>"
                    + second_column + address_you + end_tag)
    if fax_you != "":
        tags.append(first_column + "Fax</td>" + second_column + fax_you + end_tag)

    if email_you != "":
        tags.append(first_column + "Email</td>" + second_column + email_you + end_tag)

    if address_spouse != "":
        tags.append(first_column + "What is the best address to send your spouse official court documents?</td>"
                    + second_column + address_spouse + end_tag)
    if fax_spouse != "":
        tags.append(first_column + "Fax</td>" + second_column + fax_spouse + end_tag)

    if email_spouse != "":
        tags.append(first_column + "Email</td>" + second_column + email_spouse + end_tag)

    if effective_date != "":
        tags.append(first_column + "Divorce is to take effect on </td>" + second_column + effective_date + end_tag)

    return ''.join(tags)


@register.simple_tag
def marriage_tag(source):
    """
        Reformat your_marriage step
        Also show/hide optional questions
    """
    show_all = False
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    marriage_location = ""
    married_date = ""
    married_date_q = ""
    common_law_date = ""
    common_law_date_q = ""
    marital_status_you = ""
    marital_status_you_q = ""
    marital_status_spouse = ""
    marital_status_spouse_q = ""

    for item in source:
        q_id = item['question_id']
        value = item['value']
        q_name = item['question__name']

        if q_id == 'married_marriage_like' and value == 'Legally married':
            show_all = True
        elif q_id == 'when_were_you_married':
            married_date_q = q_name
            married_date = value
        elif q_id == 'when_were_you_live_married_like':
            common_law_date_q = q_name
            common_law_date = value
        elif q_id.startswith('where_were_you_married'):
            if value == 'Other':
                continue
            marriage_location += value + '<br />'
        elif q_id == 'marital_status_before_you':
            marital_status_you_q = q_name
            marital_status_you = value
        elif q_id == 'marital_status_before_spouse':
            marital_status_spouse_q = q_name
            marital_status_spouse = value

    if show_all and married_date != "":
        tags.append(first_column + married_date_q + second_column + married_date + end_tag)
    if common_law_date != "":
        tags.append(first_column + common_law_date_q + second_column + common_law_date + end_tag)
    if show_all and marriage_location != "":
        tags.append(first_column + "Where were you married" + second_column + marriage_location + end_tag)
    if marital_status_you != "":
        tags.append(first_column + marital_status_you_q + second_column + marital_status_you + end_tag)
    if marital_status_spouse != "":
        tags.append(first_column + marital_status_spouse_q + second_column + marital_status_spouse + end_tag)

    return ''.join(tags)


@register.simple_tag
def property_tag(source):
    """
        Reformat your_property and debt step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    division = division_detail = want_other = other_detail = None

    for item in source:
        q_id = item['question_id']

        if q_id == 'deal_with_property_debt':
            division = item
        elif q_id == 'how_to_divide_property_debt':
            division_detail = item
        elif q_id == 'want_other_property_claims':
            want_other = item
        elif q_id == 'other_property_claims':
            other_detail = item

    if division:
        tags.append(first_column + division['question__name'] + second_column + division['value'] + end_tag)
    if division['value'] == "Unequal division" and division_detail:
        tags.append(first_column + division_detail['question__name'] + second_column + process_list(division_detail['value'].split('\n'), division_detail['question_id']) + end_tag)
    if want_other and other_detail:
        tags.append(first_column + other_detail['question__name'] + second_column + process_list(other_detail['value'].split('\n'), other_detail['question_id']) + end_tag)

    return ''.join(tags)


@register.simple_tag
def prequal_tag(source):
    """
        Reformat prequalification step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    marriage_status = lived_in_bc = live_at_least_year = separation_date = try_reconcile = reconciliation_period = None
    children_of_marriage = any_under_19 = financial_support = certificate = provide_later = None
    provide_later_reason = not_provide_later_reason = in_english = divorce_reason = None

    for item in source:
        q_id = item['question_id']
        if q_id == 'married_marriage_like':
            marriage_status = item
        elif q_id == 'lived_in_bc':
            lived_in_bc = item
        elif q_id == 'lived_in_bc_at_least_year':
            live_at_least_year = item
        elif q_id == 'separation_date':
            separation_date = item
        elif q_id == 'try_reconcile_after_separated':
            try_reconcile = item
        elif q_id == 'reconciliation_period':
            reconciliation_period = item
        elif q_id == 'children_of_marriage':
            children_of_marriage = item
        elif q_id == 'any_under_19':
            any_under_19 = item
        elif q_id == 'children_financial_support':
            financial_support = item
        elif q_id == 'original_marriage_certificate':
            certificate = item
        elif q_id == 'provide_certificate_later':
            provide_later = item
        elif q_id == 'provide_certificate_later_reason':
            provide_later_reason = item
        elif q_id == 'not_provide_certificate_reason':
            not_provide_later_reason = item
        elif q_id == 'marriage_certificate_in_english':
            in_english = item
        elif q_id == 'divorce_reason':
            divorce_reason = item

    if marriage_status:
        tags.append(first_column + marriage_status['question__name'] + second_column + marriage_status['value'] + end_tag)
    if lived_in_bc:
        tags.append(first_column + lived_in_bc['question__name'] + second_column + lived_in_bc['value'] + end_tag)
    if live_at_least_year:
        tags.append(first_column + live_at_least_year['question__name'] + second_column + live_at_least_year['value'] + end_tag)
    if separation_date:
        tags.append(first_column + separation_date['question__name'] + second_column + separation_date['value'] + end_tag)
    if try_reconcile:
        tags.append(first_column + try_reconcile['question__name'] + second_column + try_reconcile['value'] + end_tag)
    if try_reconcile['value'] == 'YES' and reconciliation_period:
        tags.append(first_column + reconciliation_period['question__name'] + second_column + reconciliation_period_reformat(reconciliation_period['value']) + end_tag)
    if children_of_marriage:
        tags.append(first_column + children_of_marriage['question__name'] + second_column + children_of_marriage['value'] + end_tag)
    if children_of_marriage['value'] == 'YES' and any_under_19:
        tags.append(first_column + any_under_19['question__name'] + second_column + any_under_19['value'] + end_tag)
    if children_of_marriage['value'] == 'YES' and any_under_19['value'] == 'NO' and financial_support:
        tags.append(first_column + financial_support['question__name'] + second_column + json.loads(financial_support['value'])[0] + end_tag)
    if certificate:
        tags.append(first_column + certificate['question__name'] + second_column + certificate['value'] + end_tag)
    if certificate['value'] == 'NO' and provide_later:
        tags.append(first_column + provide_later['question__name'] + second_column + provide_later['value'] + end_tag)
    if certificate['value'] == 'NO' and provide_later['value'] == 'YES' and provide_later_reason:
        tags.append(first_column + provide_later_reason['question__name'] + second_column + process_list(provide_later_reason['value'].split('\n'), provide_later_reason['question_id']) + end_tag)
    if certificate['value'] == 'NO' and provide_later['value'] == 'NO' and not_provide_later_reason:
        tags.append(first_column + not_provide_later_reason['question__name'] + second_column + process_list(not_provide_later_reason['value'].split('\n'), not_provide_later_reason['question_id']) + end_tag)
    if marriage_status['value'] == 'Living together in a marriage like relationship' and in_english:
        tags.append(first_column + in_english['question__name'] + second_column + in_english['value'] + end_tag)
    if divorce_reason:
        tags.append(first_column + divorce_reason['question__name'] + second_column + divorce_reason['value'] + end_tag)

    return ''.join(tags)


@register.simple_tag
def personal_info_tag(source):
    """
        Reformat your information and your spouse step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    name = other_name = other_name_list = last_name_born = last_name_before = None
    birthday = occupation = lived_bc = moved_bc = None

    for item in source:
        q_id = item['question_id']

        if q_id.startswith('name_'):
            name = item
        elif q_id.startswith('any_other_name_'):
            other_name = item
        elif q_id.startswith('other_name_'):
            other_name_list = item
        elif q_id.startswith('last_name_born_'):
            last_name_born = item
        elif q_id.startswith('last_name_before_married_'):
            last_name_before = item
        elif q_id.startswith('birthday_'):
            birthday = item
        elif q_id.startswith('occupation_'):
            occupation = item
        elif q_id.startswith('lived_in_bc_'):
            lived_bc = item
        elif q_id.startswith('moved_to_bc_date_'):
            moved_bc = item

    if name:
        tags.append(first_column + name['question__name'] + second_column + name['value'] + end_tag)
    if other_name:
        tags.append(first_column + other_name['question__name'] + second_column + other_name['value'] + end_tag)
    if other_name['value'] == 'YES' and other_name_list:
        tags.append(first_column + other_name_list['question__name'] + second_column + process_list(json.loads(other_name_list['value']), other_name_list['question_id']) + end_tag)
    if last_name_born:
        tags.append(first_column + last_name_born['question__name'] + second_column + last_name_born['value'] + end_tag)
    if last_name_before:
        tags.append(first_column + last_name_before['question__name'] + second_column + last_name_before['value'] + end_tag)
    if birthday:
        tags.append(first_column + birthday['question__name'] + second_column + birthday['value'] + end_tag)
    if occupation:
        tags.append(first_column + occupation['question__name'] + second_column + occupation['value'] + end_tag)
    if lived_bc['value'] == "Moved to B.C. on":
        tags.append(first_column + lived_bc['question__name'] + second_column + lived_bc['value'] + ' ' + moved_bc['value'] + end_tag)
    if lived_bc['value'] != "Moved to B.C. on" and lived_bc:
        tags.append(first_column + lived_bc['question__name'] + second_column + lived_bc['value'] + end_tag)

    return ''.join(tags)


def reconciliation_period_reformat(lst):
    """
        Reformat reconciliation period into From [dd/mm/yyyy] to [dd/mm/yyyy] format
    """
    try:
        lst = json.loads(lst)
    except:
        lst = []
    period = ""
    for f_date, t_date in lst:
        period += "From " + f_date + " to " + t_date + "<br />"
    return period
