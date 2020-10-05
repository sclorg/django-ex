import functools
import json
import re


def no_children(return_val):
    def decorator_no_children(func):
        @functools.wraps(func)
        def inner(questions_dict, *args, **kwargs):
            if questions_dict.get('children_of_marriage', '') != 'YES':
                return return_val
            return func(questions_dict, *args, **kwargs)
        return inner
    return decorator_no_children


def determine_has_children_of_marriage(questions_dict):
    return questions_dict.get('children_of_marriage', '') == 'YES'


@no_children([])
def get_children(questions_dict):
    children_json = questions_dict.get('claimant_children', '[]')
    if isinstance(children_json, dict):
        children_json = children_json.get('value', '[]')
    return json.loads(children_json)


@no_children('0')
def get_num_children_living_with(questions_dict, living_arrangement):
    assert living_arrangement in ['Lives with you', 'Lives with spouse', 'Lives with both']
    children = get_children(questions_dict)
    return str(len([child for child in children if child['child_live_with'] == living_arrangement]))


@no_children(False)
def determine_sole_custody(questions_dict):
    """ Return True if all children live with one parent """
    child_list = get_children(questions_dict)
    return (all([child['child_live_with'] == 'Lives with you' for child in child_list]) or
            all([child['child_live_with'] == 'Lives with spouse' for child in child_list]))


@no_children(False)
def determine_shared_custody(questions_dict):
    """ Return True if any children live with both parents """
    child_list = get_children(questions_dict)
    return any([child['child_live_with'] == 'Lives with both'
         for child in child_list])


@no_children(False)
def determine_split_custody(questions_dict):
    """ Return True if at least one child lives with one parent and at least one lives with the other (or both) """
    child_list = get_children(questions_dict)
    with_you = 0
    with_spouse = 0
    with_both = 0
    for child in child_list:
        if child['child_live_with'] == 'Lives with you':
            with_you += 1
        elif child['child_live_with'] == 'Lives with spouse':
            with_spouse += 1
        elif child['child_live_with'] == 'Lives with both':
            with_both += 1
    return (with_you > 0 and (with_spouse + with_both > 0) or
            with_spouse > 0 and (with_you + with_both > 0))


@no_children(False)
def determine_child_over_19_supported(questions_dict):
    has_children_over_19 = questions_dict.get('has_children_over_19', '') == 'YES'
    support = json.loads(questions_dict.get('children_financial_support', '[]'))
    supporting_children = len(support) > 0 and 'NO' not in support
    return has_children_over_19 and supporting_children


@no_children(False)
def determine_missing_undue_hardship_reasons(questions_dict):
    claiming_undue_hardship = questions_dict.get('claiming_undue_hardship', '') == 'YES'
    if claiming_undue_hardship:
        at_least_one_of = ["claimant_debts", "claimant_expenses", "supporting_non_dependents", "supporting_dependents",
                           "supporting_disabled", "undue_hardship"]
        for question in at_least_one_of:
            value = questions_dict.get(question)
            if value:
                try:
                    items = json.loads(value)
                    for item in items:
                        for key in item:
                            if item[key]:
                                return False
                except json.JSONDecodeError:
                    if value:
                        return False
        return True
    else:
        return False


@no_children('')
def determine_child_support_payor(questions_dict):
    payor = questions_dict.get('child_support_payor', '')
    if payor == 'Myself (Claimant 1)':
        return 'Claimant 1'
    elif payor == 'My Spouse (Claimant 2)':
        return 'Claimant 2'
    elif payor == 'Both myself and my spouse':
        return 'both Claimant 1 and Claimant 2'
    return ''


@no_children(False)
def determine_show_fact_sheet_f_you(questions_dict):
    """
    If claimant 1 (you) is a payor and makes over $150,000/year, show fact sheet F for claimant 1
    """
    payor = determine_child_support_payor(questions_dict)
    try:
        annual = float(questions_dict.get('annual_gross_income', 0))
    except ValueError:
        annual = 0
    return (payor == 'Claimant 1' or payor == 'both Claimant 1 and Claimant 2') and annual > 150000


@no_children(False)
def determine_show_fact_sheet_f_spouse(questions_dict):
    """
    If claimant 2 (spouse) is a payor and makes over $150,000/year, show fact sheet F for claimant 2
    """
    payor = determine_child_support_payor(questions_dict)

    try:
        annual = float(questions_dict.get('spouse_annual_gross_income', 0))
    except ValueError:
        annual = 0

    return (payor == 'Claimant 2' or payor == 'both Claimant 1 and Claimant 2') and annual > 150000


@no_children(False)
def determine_child_support_act_requirement(questions_dict):
    orders_wanted = json.loads(questions_dict.get('want_which_orders', '[]'))
    return 'Child support' in orders_wanted


@no_children(False)
def determine_missing_extraordinary_expenses(questions_dict):
    special_expenses_keys = ["child_care_expenses",
                             "children_healthcare_premiums",
                             "health_related_expenses",
                             "extraordinary_educational_expenses",
                             "post_secondary_expenses",
                             "extraordinary_extracurricular_expenses"]

    if questions_dict.get('special_extraordinary_expenses') == 'YES':
        for special_expense in special_expenses_keys:
            value = questions_dict.get(special_expense, 0)
            try:
                as_num = float(value)
                if as_num > 0:
                    return False
            except ValueError:
                pass
        return True
    else:
        return False


@no_children(False)
def determine_show_children_live_with_others(questions_dict):
    has_children_under_19 = questions_dict.get('has_children_under_19', '') == 'YES'
    child_over_19_supported = determine_child_over_19_supported(questions_dict)
    return has_children_under_19 or child_over_19_supported


def orders_wanted(questions_dict):
    return json.loads(questions_dict.get('want_which_orders', '[]'))


def determine_spousal_support_orders_wanted(questions_dict):
    return 'Spousal support' in orders_wanted(questions_dict)


def determine_property_debt_orders_wanted(questions_dict):
    return 'Division of property and debts' in orders_wanted(questions_dict)


def determine_other_orders_wanted(questions_dict):
    return 'Other orders' in orders_wanted(questions_dict)


def get_cleaned_response_value(response):
    if response is None:
        return None
    response = response.strip()
    search_text = response.replace('also known as', '')
    if re.search(r'\w+', search_text):
        return response
    return None
