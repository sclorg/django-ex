from collections import OrderedDict

from django import template
import json

from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

NO_ANSWER = 'No answer'
MISSING_RESPONSE = mark_safe('<div class="table-error"><span class="warning">MISSING REQUIRED FIELD</span></div>') # nosec

register = template.Library()


@register.simple_tag
def reformat_value(source):
    """
    Reformat user response on summary page
    Cases:
    - If there is a missing field, return error html
    - If value is a json list:
        Either return the only item
        Or make it into bullet point form
    - If it's a text area:
        For certain fields, make it into bullet points
        For others, convert \n to <br>
    - Otherwise, return the original value
    """
    if source['error']:
        return MISSING_RESPONSE
    elif not source['value']:
        return NO_ANSWER
    question_key = source['question_id']
    try:
        json_list = json.loads(source['value'])
        return process_json_list(question_key, json_list)
    except:
        if question_key in ['spouse_support_details', 'other_orders_detail']:
            return reformat_textarea(source)
        elif '\n' in source['value']:
            return reformat_textarea(source, as_ul=False)
        return source['value']


def process_json_list(question_key, json_list):
    """
    Convert a json list to html list, handling special question formats
    """
    assert isinstance(json_list, list)
    if question_key.startswith('other_name_'):
        list_items = get_other_name_tags(json_list)
    elif question_key == 'reconciliation_period':
        list_items = get_reconciliation_period_tags(json_list)
    elif question_key == 'claimant_children':
        return get_claimant_children_tags(json_list)
    elif 'address' in question_key:
        tag = format_html_join(
            '\n',
            '{0}<br/>',
            ((value, '') for value in json_list))
        return tag
    else:
        list_items = format_html_join(
                    '\n',
                    '<li>{0}</li>',
                    ((value, '') for value in json_list if value and not value.isspace()))
    tag = format_html(
        '<ul>{}</ul>',
        list_items)

    return tag


def get_other_name_tags(json_list):
    if len(json_list) > 0 and len(json_list[0]) == 5:
        # new json format with fielded names
        return format_html_join(
            '\n',
            '<li>{} {} {} {} {}</li>',
            ((alias_type, last_name, given1, given2, given3) for alias_type, last_name, given1, given2, given3 in json_list if last_name))
    else:
        # old json format with unfielded names
        return format_html_join(
            '\n',
            '<li>{} {}</li>',
            ((alias_type, value) for alias_type, value in json_list if value))


def get_reconciliation_period_tags(json_list):
    list_items = format_html_join(
        '\n',
        '<li>From {} to {}</li>',
        (date_range for date_range in json_list))
    return list_items


def get_claimant_children_tags(json_list):
    child_counter = 1
    tags = ''
    for child in json_list:
        tags = format_html(
            '{}{}{}{}{}{}{}',
            tags,
            format_review_row_heading('Child {}'.format(child_counter), 'review-child-heading'),
            format_row('Child\'s name', child['child_name']),
            format_row('Birth date', child['child_birth_date']),
            format_row('Child now living with', child['child_live_with']),
            format_row('Relationship to yourself (claimant 1)', child['child_relationship_to_you']),
            format_row('Relationship to your spouse (claimant 2)', child['child_relationship_to_spouse']))
        child_counter = child_counter + 1
    return tags


def reformat_textarea(source, as_ul=True):
    """
    Takes a textarea value (string with \n) and converts either into html with <br> tags or a list
    """
    response = source['value']
    if not response:
        return NO_ANSWER
    text_list = response.split('\n')
    if len(text_list) > 1:
        if as_ul:
            list_items = format_html_join(
                        '\n',
                        '<li>{0}</li>',
                        ((value, '') for value in text_list if value))
            tag = format_html(
                '<ul>{}</ul>',
                list_items)
        else:
            tag = format_html_join(
                '\n',
                '<p>{0}<p/>',
                ((value, '') for value in text_list))
        return tag
    else:
        return text_list.pop()


def format_row(question, response):
    """ Used for children sub-section tables """
    return format_html(
        '<tr><td class="table-bordered" style="padding-right: 5%">{0}</td><td class="table-bordered value-column">{1}</td></tr>',
        question,
        response)


def format_review_row_heading(title, style="", substep=None):
    """ Used for children sub-section tables """
    if substep:
        url = reverse('question_steps', args=['children', substep])
        extra_html = mark_safe(f'<span class="review-buttons"><a href="{url}">Edit</a></span>') # nosec
    else:
        extra_html = ''
    return format_html(
        '<tr><td colspan="2" class="table-bordered {1}"><b>{0}</b>{2}</td></tr>',
        title,
        style,
        extra_html,
    )


def format_fact_sheet(title, url, value):
    return format_html(
        '<tr><td class="table-bordered"><a href="{}"><b>{}</b></a></td><td class="table-bordered">{}</td></tr>',
        url,
        title,
        value
    )


@register.simple_tag(takes_context=True)
def format_children(context, source):
    substep_to_heading = {
        'your_children': 'Children details',
        'income_expenses': 'Income & expenses',
        'facts': 'Payor & Fact Sheets',
        'payor_medical': 'Medical & other expenses',
        'what_for': 'What are you asking for?',
    }
    question_to_heading = OrderedDict()
    question_to_heading['your_children'] = [
        'claimant_children'
    ]
    question_to_heading['income_expenses'] = [
        'how_will_calculate_income',
        'annual_gross_income',
        'spouse_annual_gross_income',
        'payor_monthly_child_support_amount',
        'special_extraordinary_expenses',
        'Special or Extraordinary Expenses (Fact Sheet A)',
        'describe_order_special_extra_expenses'
    ]
    question_to_heading['facts'] = [
        'Shared Living Arrangement (Fact Sheet B)',
        'Split Living Arrangement (Fact Sheet C)',
        'child_support_payor',
        'Child(ren) 19 Years or Older (Fact Sheet D)',
        'Income over $150,000 (Fact Sheet F)',
        'claiming_undue_hardship',
        'Undue Hardship (Fact Sheet E)'
    ]
    question_to_heading['payor_medical'] = [
        'medical_coverage_available',
        'whose_plan_is_coverage_under',
        'child_support_payments_in_arrears',
        'child_support_arrears_amount'
    ]
    question_to_heading['what_for'] = [
        'child_support_in_order',
        # 'order_monthly_child_support_amount',
        'child_support_in_order_reason',
        'claimants_agree_to_child_support_amount',
        'child_support_payment_special_provisions',
        'agree_to_child_support_amount',
        'have_separation_agreement',
        'have_court_order',
        'what_parenting_arrangements',
        'want_parenting_arrangements',
        'order_respecting_arrangement',
        'order_for_child_support',
        'child_support_act'
    ]

    fact_sheet_mapping = OrderedDict()
    fact_sheet_mapping['Special or Extraordinary Expenses (Fact Sheet A)'] = reverse('question_steps', args=['children', 'income_expenses'])
    fact_sheet_mapping['Shared Living Arrangement (Fact Sheet B)'] = reverse('question_steps', args=['children', 'facts'])
    fact_sheet_mapping['Split Living Arrangement (Fact Sheet C)'] = reverse('question_steps', args=['children', 'facts'])
    fact_sheet_mapping['Child(ren) 19 Years or Older (Fact Sheet D)'] = reverse('question_steps', args=['children', 'facts'])
    fact_sheet_mapping['Undue Hardship (Fact Sheet E)'] = reverse('question_steps', args=['children', 'facts'])
    fact_sheet_mapping['Income over $150,000 (Fact Sheet F)'] = reverse('question_steps', args=['children', 'facts'])

    tags = format_html('<tbody>')
    # process mapped questions first
    working_source = source.copy()
    for substep, questions in question_to_heading.items():
        title = substep_to_heading[substep]
        tags = format_html(
            '{}{}',
            tags,
            format_review_row_heading(title, substep=substep))

        for question in questions:
            if question in fact_sheet_mapping:
                show_fact_sheet = False
                fact_sheet_error = False
                if question == 'Special or Extraordinary Expenses (Fact Sheet A)' and context['derived']['show_fact_sheet_a']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_a_error']
                elif question == 'Shared Living Arrangement (Fact Sheet B)' and context['derived']['show_fact_sheet_b']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_b_error']
                elif question == 'Split Living Arrangement (Fact Sheet C)' and context['derived']['show_fact_sheet_c']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_c_error']
                elif question == 'Child(ren) 19 Years or Older (Fact Sheet D)' and context['derived']['show_fact_sheet_d']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_d_error']
                elif question == 'Undue Hardship (Fact Sheet E)' and context['derived']['show_fact_sheet_e']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_e_error']
                elif question == 'Income over $150,000 (Fact Sheet F)' and context['derived']['show_fact_sheet_f']:
                    show_fact_sheet = True
                    fact_sheet_error = context['derived']['fact_sheet_f_error']

                if show_fact_sheet and len(fact_sheet_mapping[question]):
                    if fact_sheet_error:
                        value = MISSING_RESPONSE
                    else:
                        value = 'Complete'
                    tags = format_html(
                        '{}{}',
                        tags,
                        format_fact_sheet(question, fact_sheet_mapping[question], value))
            else:
                item_list = list(filter(lambda x: x['question_id'] == question, working_source))

                if len(item_list):
                    item = item_list.pop()
                    q_id = item['question_id']
                    if q_id in questions:
                        if q_id == 'describe_order_special_extra_expenses':
                            pass
                        if q_id == 'payor_monthly_child_support_amount':
                            # Only display this field if it is sole custody
                            if not context['derived']['sole_custody']:
                                continue

                        question_name = item['question__name']
                        if question == 'child_support_in_order':
                            question_name = '{} {}'.format(question_name, context['derived']['child_support_payor_by_name'])
                            if item['value'] == 'MATCH':
                                item['value'] = '{:.2f}'.format(float(context['derived']['guideline_amounts_difference_total']))
                            elif item['value'] == 'DIFF':
                                amount = list(filter(lambda x: x['question_id'] == 'order_monthly_child_support_amount', working_source))
                                amount = amount.pop()
                                item['value'] = '{:.2f}'.format(float(amount['value']))

                        tags = format_html('{}{}', tags, format_row(question_name, reformat_value(item)))
        tags = format_html('{}</tbody> <tbody class="review-table-spacer">', tags)
    tags = format_html('{}</tbody>', tags)
    return tags


@register.simple_tag
def combine_address(source):
    tags = ''

    address_you = []
    address_you_name = "What is the best address to send you official court documents?"
    address_you_error = False
    address_spouse = []
    address_spouse_name = "What is the best address to send your spouse official court documents?"
    address_spouse_error = False
    take_effect_on_item = None

    for item in source:
        q_id = item['question_id']
        if 'address' in q_id and 'email' not in q_id and 'fax' not in q_id:
            if 'you' in q_id:
                if address_you_error:
                    continue
                elif item['error']:
                    address_you_error = True
                    tags = format_table_data(tags, address_you_name, MISSING_RESPONSE)
                    continue
                elif item['value'] and item['value'] != 'Other':
                    address_you.append(item['value'])
                if 'postal_code' in q_id:
                    tags = format_table_data(tags, address_you_name, process_json_list(q_id, address_you))
                continue
            else:
                if address_spouse_error:
                    continue
                elif item['error']:
                    address_spouse_error = True
                    tags = format_table_data(tags, address_spouse_name, MISSING_RESPONSE)
                    continue
                elif item['value'] and item['value'] != 'Other':
                    address_spouse.append(item['value'])
                if 'postal_code' in q_id:
                    tags = format_table_data(tags, address_spouse_name, process_json_list(q_id, address_spouse))
                continue
        elif q_id == 'divorce_take_effect_on':
            take_effect_on_item = item
            if item['value'] == 'specific date':
                continue
        elif q_id == 'divorce_take_effect_on_specific_date':
            item['question__name'] = take_effect_on_item['question__name']
        tags = format_question_for_table(tags, item)

    return tags


@register.simple_tag(takes_context=True)
def marriage_tag(context, source):
    tags = ''
    marriage_location = []
    marriage_country_is_other = False
    skip_location = False
    for item in source:
        q_id = item['question_id']
        if q_id.startswith('where_were_you_married') and not skip_location:
            if item['error']:
                skip_location = True
                tags = format_table_data(tags, "Where were you married?", MISSING_RESPONSE)
                continue
            elif q_id == 'where_were_you_married_country' and item['value'] == 'Other':
                marriage_country_is_other = True
                continue
            elif item['value']:
                marriage_location.append(item['value'])

            # Insert in the right spot in table. Either country is the last item (if US or Canada) or other country is last
            us_or_canada = not marriage_country_is_other and q_id == 'where_were_you_married_country'
            other_country = marriage_country_is_other and q_id == 'where_were_you_married_other_country'
            if us_or_canada or other_country:
                tags = format_table_data(tags, "Where were you married?", process_json_list('married_address', marriage_location))
        else:
            tags = format_question_for_table(tags, item)

    return tags


@register.simple_tag
def prequal_tag(source):
    tags = ''
    for item in source:
        if item['question_id'] == 'divorce_reason':
            if item['value'] == 'live separate':
                item['value'] = 'Lived apart for one year'
            elif item['value'] == 'other':
                item['value'] = 'Other reasons (grounds)'
        tags = format_question_for_table(tags, item)

    return tags


@register.simple_tag
def personal_info_tag(source):
    tags = ''
    lived_in_bc_item = None
    for item in source:
        q_id = item['question_id']
        moved_to_bc_value = "Moved to B.C. on"
        if q_id.startswith('lived_in_bc_') and item['value'] == moved_to_bc_value:
            lived_in_bc_item = item
            continue
        elif q_id.startswith('moved_to_bc_date_'):
            item['question__name'] = lived_in_bc_item['question__name']
            item['value'] = f"{moved_to_bc_value} {item['value']}"
        tags = format_question_for_table(tags, item)
    return tags


def format_question_for_table(tags, question):
    name = question['question__name']
    response = reformat_value(question)
    return format_table_data(tags, name, response)


def format_table_data(tags, question, response):
    return format_html(
        '{}<tr><td style="padding-right: 5%">{}</td><td class="value-column">{}</td></tr>',
        tags,
        question,
        response)
