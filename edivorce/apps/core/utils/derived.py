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
    'has_children_of_marriage',
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
    'show_fact_sheet_f_you',
    'show_fact_sheet_f_spouse',
    'has_fact_sheets',
    'schedule_1_amount',
    'child_support_payor',
    'child_support_payor_by_name',
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
    'total_child_support_payment_a',
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
    'medical_covered_by_1',
    'medical_covered_by_2',
    'pursuant_parenting_arrangement',
    'pursuant_child_support',
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


def has_children_of_marriage(responses, derived):
    """ Returns whether or not the their are children of marriage for claim"""

    return responses.get('children_of_marriage', '') == 'YES'


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

    return responses.get('special_extraordinary_expenses', '') == 'YES'


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

    try:
        children_over_19 = float(responses.get('number_children_over_19', 0))
    except ValueError:
        children_over_19 = 0

    support = json.loads(responses.get('children_financial_support', '[]'))
    return (len(support) > 0 and children_over_19 > 0 and
            'NO' not in support and has_children_of_marriage(responses, derived))


def show_fact_sheet_e(responses, derived):
    """
    If the claimant is claiming undue hardship, Fact Sheet E is indicated.
    """

    return responses.get('claiming_undue_hardship', '') == 'YES'


def show_fact_sheet_f(responses, derived):
    """
    If one of the claimants earns over $150,000, Fact Sheet F is indicated.
    """
    return show_fact_sheet_f_you(responses, derived) or show_fact_sheet_f_spouse(responses, derived)


def show_fact_sheet_f_you(responses, derived):
    """

    :param responses:
    :param derived:
    :return:
    """
    payor = child_support_payor(responses, derived)

    try:
        annual = float(responses.get('annual_gross_income', 0))
    except ValueError:
        annual = 0

    return (payor == 'Claimant 1' or payor == 'both Claimant 1 and Claimant 2') and annual > 150000


def show_fact_sheet_f_spouse(responses, derived):
    """

    :param responses:
    :param derived:
    :return:
    """
    payor = child_support_payor(responses, derived)

    try:
        annual = float(responses.get('spouse_annual_gross_income', 0))
    except ValueError:
        annual = 0

    return (payor == 'Claimant 2' or payor == 'both Claimant 1 and Claimant 2') and annual > 150000


def has_fact_sheets(responses, derived):
    """ Return whether or not the user is submitting fact sheets """

    return any([derived['show_fact_sheet_b'], derived['show_fact_sheet_c'],
                derived['show_fact_sheet_d'], derived['show_fact_sheet_e'],
                derived['show_fact_sheet_f'], ])


def schedule_1_amount(responses, derived):
    """ Return the amount as defined in schedule 1 for child support """

    try:
        return float(responses.get('payor_monthly_child_support_amount', 0))
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


def child_support_payor_by_name(responses, derived):
    """ Return the payor by name"""

    payor = 'the payor'
    support_payor = child_support_payor(responses, derived)
    if support_payor == 'Claimant 1':
        payor = responses.get('name_you', support_payor)
    elif support_payor == 'Claimant 2':
        payor = responses.get('name_spouse', support_payor)
    elif support_payor == 'both Claimant 1 and Claimant 2':
        payor = '{} and {}'.format(responses.get('name_you', 'myself'),
                                   responses.get('name_spouse', 'my spouse'))
    return payor


def annual_child_care_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of child care expense """

    try:
        return float(responses.get('annual_child_care_expenses', 0))
    except ValueError:
        return 0


def annual_children_healthcare_premiums(responses, derived):
    """ Return the annual cost of the monthly cost of child health care premiums """

    try:
        return float(responses.get('annual_children_healthcare_premiums', 0))
    except ValueError:
        return 0


def annual_health_related_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of health related expense """

    try:
        return float(responses.get('annual_health_related_expenses', 0))
    except ValueError:
        return 0


def annual_extraordinary_educational_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of educational expense """

    try:
        return float(responses.get('annual_extraordinary_educational_expenses', 0))
    except ValueError:
        return 0


def annual_post_secondary_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of post secondary expense """

    try:
        return float(responses.get('annual_post_secondary_expenses', 0))
    except ValueError:
        return 0


def annual_extraordinary_extracurricular_expenses(responses, derived):
    """ Return the annual cost of the monthly cost of education expense """

    try:
        return float(responses.get('annual_extraordinary_extracurricular_expenses', 0))
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

    try:
        return float(responses.get('annual_total_section_seven_expenses', 0))
    except ValueError:
        return 0


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
        share = float(responses.get('your_proportionate_share_percent', 0))
    except ValueError:
        share = 0

    return share


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

    try:
        share = float(responses.get('spouse_proportionate_share_percent', 0))
    except ValueError:
        share = 0

    return share


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


def total_child_support_payment_a(response, derived):
    """ Return the total monthly child support payable by the payor for Fact Sheet A """
    total = 0
    sole_custody = (all([child['child_live_with'] == 'Lives with you' for child in derived['children']]) or
                    all([child['child_live_with'] == 'Lives with spouse' for child in derived['children']]))

    if sole_custody:
        total += derived['schedule_1_amount']
    else:
        if derived['show_fact_sheet_b']:
            total += guideline_amounts_difference(response, derived)
        if derived['show_fact_sheet_c']:
            total += guideline_amounts_difference(response, derived)

    if derived['show_fact_sheet_a']:
        if derived['child_support_payor'] == 'Claimant 1':
            total += derived['claimant_1_share']
        elif derived['child_support_payor'] == 'Claimant 2':
            total += derived['claimant_2_share']
        else:
            total += derived['total_section_seven_expenses']

    return total


def claimant_debts(responses, derived):
    """ Return the parsed array of claimant_debts """

    try:
        return json.loads(responses.get('claimant_debts', '[]'))
    except ValueError:
        return []


def claimant_expenses(responses, derived):
    """ Return the parsed array of claimant_expenses """

    try:
        return json.loads(responses.get('claimant_expenses', '[]'))
    except ValueError:
        return []


def supported_dependents(responses, derived):
    """ Return the parsed array of supporting_dependents """

    try:
        return json.loads(responses.get('supporting_dependents', '[]'))
    except ValueError:
        return []


def supported_non_dependents(responses, derived):
    """ Return the parsed array of supporting_non_dependents """

    try:
        return json.loads(responses.get('supporting_non_dependents', '[]'))
    except ValueError:
        return []


def supported_disabled(responses, derived):
    """ Return the parsed array of supporting_disabled """

    try:
        return json.loads(responses.get('supporting_disabled', '[]'))
    except ValueError:
        return []


def others_income(responses, derived):
    """ Return the parsed array of income_others """

    try:
        return json.loads(responses.get('income_others', '[]'))
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


def medical_covered_by_1(responses, derived):
    """ Return whether the children are covered under Claimant 1's plan """

    if responses.get('medical_coverage_available', 'NO') == 'YES':
        return 'My plan' in responses.get('whose_plan_is_coverage_under', '')
    return False


def medical_covered_by_2(responses, derived):
    """ Return whether the children are covered under Claimant 2's plan """

    if responses.get('medical_coverage_available', 'NO') == 'YES':
        return 'Spouse' in responses.get('whose_plan_is_coverage_under', '')
    return False


def pursuant_parenting_arrangement(responses, derived):
    """
    Return a list of parenting arrangement bullet points, prefaced by the
    correct 'pursuant to' phrase.
    """

    act = responses.get('child_support_act', '')
    act = 'Pursuant to %s,' % act if act != '' else act
    try:
        arrangements = responses.get('order_respecting_arrangement', '').split('\n')
        return ['%s %s' % (act, arrangement.strip())
                for arrangement in arrangements
                if len(arrangement.strip()) > 0]
    except ValueError:
        return []


def pursuant_child_support(responses, derived):
    """
    Return a list of child support bullet points, prefaced by the correct
    'pursuant to' phrase.
    """

    act = responses.get('child_support_act', '')
    act = 'Pursuant to %s,' % act if act != '' else act
    try:
        arrangements = responses.get('order_for_child_support', '').split('\n')
        return ['%s %s' % (act, arrangement.strip())
                for arrangement in arrangements
                if len(arrangement.strip()) > 0]
    except ValueError:
        return []
