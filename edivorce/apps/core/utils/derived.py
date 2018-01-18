# pylint: disable=W0613,C0103
"""Values derived from a user's responses.

This module provides functions to take a set of responses from a user and create
a set of derived values that are consistent with the user's responses.  This is
done, in part, to centralize the logic for getting such derived values (such as
whether or not to show a particular fact sheet).

The general usage is to add to the context of a template by calling
``get_derived_data`` on the user responses and including the resulting dict
under the _derived_ key.
"""

import json

# This array is order sensitive: later functions may depend on values from
# earlier ones
DERIVED_DATA = [
    'orders_wanted',
    'children',
    'wants_divorce_order',
    'wants_spousal_support',
    'wants_property_division',
    'wants_child_support',
    'wants_other_orders',
    'show_fact_sheet_a',
    'show_fact_sheet_b',
    'show_fact_sheet_c',
    'show_fact_sheet_d',
    'show_fact_sheet_e',
    'show_fact_sheet_f',
    'has_fact_sheets',
    'schedule_1_amount',
    'child_support_payor',
    'annual_child_care_expenses',
    'annual_children_healthcare_premiums',
    'annual_health_related_expenses',
    'annual_extraordinary_educational_expenses',
    'annual_post_secondary_expenses',
    'annual_extraordinary_extracurricular_expenses',
    'total_section_seven_expenses',
    'annual_total_section_seven_expenses',
    'total_gross_income',
    'claimant_1_share_proportion',
    'claimant_1_share',
    'claimant_2_share_proportion',
    'claimant_2_share',
    'payor_section_seven_expenses',
    'total_monthly_support_1_and_a',
    'guideline_amounts_difference',
    'claimant_debts',
    'claimant_expenses',
    'supported_dependents',
    'supported_non_dependents',
    'supported_disabled',
    'others_income',
    'total_others_income',
    'high_income_amount',
    'total_monthly_b',
]


def get_derived_data(responses):
    """ Return a dict of data derived from the user's responses """

    functions = globals()
    derived = {}
    for func in DERIVED_DATA:
        derived[func] = functions[func](responses, derived)
    return derived


def orders_wanted(responses, derived):
    """ Return a list of orders the user has indicated """

    return json.loads(responses.get('want_which_orders', '[]'))


def children(responses, derived):
    """ Return a list of child dicts, parsed from ``claimants_children`` """

    return json.loads(responses.get('claimant_children', '[]'))


def wants_divorce_order(responses, derived):
    """ Return whether or not the user wants an order for divorce """

    return 'A legal end to the marriage' in derived['orders_wanted']


def wants_spousal_support(responses, derived):
    """ Return whether or not the user wants an order for spousal support """

    return 'Spousal support' in derived['orders_wanted']


def wants_property_division(responses, derived):
    """
    Return whether or not the user wants an order for division of property and
    debts
    """

    return 'Division of property and debts' in responses.get('want_which_orders', '')


def wants_child_support(responses, derived):
    """ Return whether or not the user wants an order for child_support """

    return 'Child support' in derived['orders_wanted']


def wants_other_orders(responses, derived):
    """ Return whether or not the user wants other orders """

    return 'Other orders' in derived['orders_wanted']


def show_fact_sheet_a(responses, derived):
    """
    If the claimant is claiming special extraordinary expenses, Fact Sheet A is
    indicated.
    """

    expenses = json.loads(responses.get('special_extraordinary_expenses', '[]'))
    return len(expenses) > 0 and "None" not in expenses


def show_fact_sheet_b(responses, derived):
    """
    If any child lives with both parents, custody is shared, so Fact Sheet B
    is indicated.
    """

    return any([child['child_live_with'] == 'Lives with both'
                for child in derived['children']])


def show_fact_sheet_c(responses, derived):
    """
    If any child lives with one parent and there's another child who lives with
    the other parent or is shared, Fact Sheet C is indicated.
    """

    with_you = 0
    with_spouse = 0
    with_both = 0
    for child in derived['children']:
        if child['child_live_with'] == 'Lives with you':
            with_you += 1
        elif child['child_live_with'] == 'Lives with spouse':
            with_spouse += 1
        elif child['child_live_with'] == 'Lives with both':
            with_both += 1
    return (with_you > 0 and (with_spouse + with_both > 0) or
            with_spouse > 0 and (with_you + with_both > 0))


def show_fact_sheet_d(responses, derived):
    """
    If a claimaint is claiming financial support for a child of the marriage
    over 19, Fact Sheet D is indicated.
    """

    support = json.loads(responses.get('children_financial_support', '[]'))
    return len(support) > 0 and 'NO' not in support and responses.get('children_of_marriage', '') == 'YES'


def show_fact_sheet_e(responses, derived):
    """
    If the claimant is claiming undue hardship, Fact Sheet E is indicated.
    """

    return responses.get('claiming_undue_hardship', '') == 'YES'


def show_fact_sheet_f(responses, derived):
    """
    If one of the claimants earns over $150,000, Fact Sheet F is indicated.
    """

    try:
        annual = float(responses.get('annual_gross_income', 0))
    except ValueError:
        annual = 0

    try:
        spouses = float(responses.get('spouse_annual_gross_income', 0))
    except ValueError:
        spouses = 0

    return annual > 150000 or spouses > 150000


def has_fact_sheets(responses, derived):
    """ Return whether or not the user is submitting fact sheets """

    return any([derived['show_fact_sheet_a'], derived['show_fact_sheet_b'],
                derived['show_fact_sheet_c'], derived['show_fact_sheet_d'],
                derived['show_fact_sheet_e'], derived['show_fact_sheet_f'], ])


def schedule_1_amount(responses, derived):
    """ Return the amount as defined in schedule 1 for child support """

    try:
        return float(responses.get('order_monthly_child_support_amount', 0))
    except ValueError:
        return 0


def child_support_payor(responses, derived):
    """ Return the payor phrased for the affidavit """

    payor = responses.get('child_support_payor', '')
    if payor == 'Myself (Claimant 1)':
        return 'Claimant 1'
    elif payor == 'My Spouse (Claimant 2)':
        return 'Claimant 2'
    elif payor == 'Both myself and my spouse':
        return 'both Claimant 1 and Claimant 2'

    return ''


def annual_child_care_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of child care expense """

    try:
        return 12 * float(responses.get('child_care_expenses', 0))
    except ValueError:
        return 0


def annual_children_healthcare_premiums(responses, derived):
    """ Return the annual cost of the monthly cost of child health care premiums """

    try:
        return 12 * float(responses.get('children_healthcare_premiums', 0))
    except ValueError:
        return 0


def annual_health_related_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of health related expense """

    try:
        return 12 * float(responses.get('health_related_expenses', 0))
    except ValueError:
        return 0


def annual_extraordinary_educational_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of educational expense """

    try:
        return 12 * float(responses.get('extraordinary_educational_expenses', 0))
    except ValueError:
        return 0


def annual_post_secondary_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of post secondary expense """

    try:
        return 12 * float(responses.get('post_secondary_expenses', 0))
    except ValueError:
        return 0


def annual_extraordinary_extracurricular_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of education expense """

    try:
        return 12 * float(responses.get('extraordinary_extracurricular_expenses', 0))
    except ValueError:
        return 0


def total_section_seven_expenses(responses, derived):
    """ Return the monthly cost of section 7 expense """

    try:
        return float(responses.get('total_section_seven_expenses', 0))
    except ValueError:
        return 0


def payor_section_seven_expenses(responses, derived):
    """ Return the monthly cost of section 7 expense for the identified payor """

    if derived['child_support_payor'] == 'Claimant 1':
        return derived['claimant_1_share']
    elif derived['child_support_payor'] == 'Claimant 2':
        return derived['claimant_2_share']
    return derived['total_section_seven_expenses']


def annual_total_section_seven_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of section 7 expense """

    return 12 * derived['total_section_seven_expenses']


def total_gross_income(responses, derived):
    """ Return the total gross income of both claimants """

    try:
        claimant_1 = float(responses.get('annual_gross_income', 0))
    except ValueError:
        claimant_1 = 0

    try:
        claimant_2 = float(responses.get('spouse_annual_gross_income', 0))
    except ValueError:
        claimant_2 = 0

    return claimant_1 + claimant_2


def claimant_1_share_proportion(responses, derived):
    """
    Return the proportionate share of claimant 1 for child support, based on
    annual income.
    """

    try:
        income = float(responses.get('annual_gross_income', 0))
    except ValueError:
        income = 0

    if derived['total_gross_income'] == 0:
        return 0
    return income / derived['total_gross_income'] * 1000 // 1 / 10


def claimant_1_share(responses, derived):
    """
    Return the proportionate amount of claimant 1 for child support, based on
    annual income.
    """

    proportion = derived['claimant_1_share_proportion'] / 100
    return derived['total_section_seven_expenses'] * proportion


def claimant_2_share_proportion(responses, derived):
    """
    Return the proportionate share of claimant 2 for child support, based on
    annual income.
    """

    if derived['total_gross_income'] == 0:
        return 0
    return 100 - derived['claimant_1_share_proportion'] * 10 // 1 / 10


def claimant_2_share(responses, derived):
    """
    Return the proportionate amount of claimant 2 for child support, based on
    annual income.
    """

    proportion = derived['claimant_2_share_proportion'] / 100
    return derived['total_section_seven_expenses'] * proportion


def total_monthly_support_1_and_a(responses, derived):
    """ Return the combined schedule 1 and section 7 monthly amounts """

    total = derived['schedule_1_amount']
    if derived['child_support_payor'] == 'Claimant 1':
        total += derived['claimant_1_share']
    elif derived['child_support_payor'] == 'Claimant 2':
        total += derived['claimant_2_share']
    else:
        total += derived['total_section_seven_expenses']
    return total


def guideline_amounts_difference(responses, derived):
    """
    Return the difference between the guideline amounts to be paid by
    claimant 1 and claimant 2
    """

    try:
        amount_1 = float(responses.get('your_child_support_paid', 0))
    except ValueError:
        amount_1 = 0

    try:
        amount_2 = float(responses.get('your_spouse_child_support_paid', 0))
    except ValueError:
        amount_2 = 0

    return abs(amount_1 - amount_2)


def claimant_debts(responses, derived):
    """ Return the parsed array of claimant_debts """

    try:
        return json.loads(responses.get('claimant_debts', []))
    except ValueError:
        return []


def claimant_expenses(responses, derived):
    """ Return the parsed array of claimant_expenses """

    try:
        return json.loads(responses.get('claimant_expenses', []))
    except ValueError:
        return []


def supported_dependents(responses, derived):
    """ Return the parsed array of supporting_dependents """

    try:
        return json.loads(responses.get('supporting_dependents', []))
    except ValueError:
        return []


def supported_non_dependents(responses, derived):
    """ Return the parsed array of supporting_non_dependents """

    try:
        return json.loads(responses.get('supporting_non_dependents', []))
    except ValueError:
        return []


def supported_disabled(responses, derived):
    """ Return the parsed array of supporting_disabled """

    try:
        return json.loads(responses.get('supporting_disabled', []))
    except ValueError:
        return []


def others_income(responses, derived):
    """ Return the parsed array of income_others """

    try:
        return json.loads(responses.get('income_others', []))
    except ValueError:
        return []


def total_others_income(responses, derived):
    """ Return the total of other incomes """

    total = 0.0

    for income in derived['others_income']:
        try:
            total += float(income['income_others_amount'])
        except ValueError:
            pass

    return total


def high_income_amount(responses, derived):
    """ Return the guidelines table amount for a high income earner """

    try:
        under = float(responses.get('child_support_amount_under_high_income', 0))
    except ValueError:
        under = 0

    try:
        over = float(responses.get('amount_income_over_high_income_limit', 0))
    except ValueError:
        over = 0

    return under + over


def total_monthly_b(responses, derived):
    """ Return the total amount payable by the payor for Fact Sheet B """

    difference = derived['guideline_amounts_difference']

    return difference
