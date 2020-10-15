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

from edivorce.apps.core.utils import conditional_logic
from edivorce.apps.core.templatetags import format_utils

# This array is order sensitive: later functions may depend on values from
# earlier ones
from edivorce.apps.core.utils.conditional_logic import (
    determine_child_support_payor,
    determine_show_fact_sheet_f_spouse,
    determine_show_fact_sheet_f_you,
    determine_missing_extraordinary_expenses
)

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
    'fact_sheet_a_error',
    'show_fact_sheet_b',
    'fact_sheet_b_error',
    'show_fact_sheet_c',
    'fact_sheet_c_error',
    'show_fact_sheet_d',
    'fact_sheet_d_error',
    'show_fact_sheet_e',
    'fact_sheet_e_error',
    'show_fact_sheet_f_you',
    'show_fact_sheet_f_spouse',
    'show_fact_sheet_f',
    'fact_sheet_f_error',
    'has_fact_sheets',
    'child_support_payor_b',
    'child_support_payor_c',
    'guideline_amounts_difference_b',
    'guideline_amounts_difference_c',
    'guideline_amounts_difference_total',
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
    'child_support_acts',
    'pursuant_parenting_arrangement',
    'pursuant_child_support',
    'sole_custody',
    'number_of_children',
    'number_of_children_claimant',
    'number_of_children_claimant_spouse',
    'any_errors',
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
    return conditional_logic.orders_wanted(responses)


def children(responses, derived):
    """ Return a list of child dicts, parsed from ``claimants_children`` """

    return json.loads(responses.get('claimant_children', '[]'))


def has_children_of_marriage(responses, derived):
    return conditional_logic.determine_has_children_of_marriage(responses)


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


def fact_sheet_a_error(responses, derived):
    return determine_missing_extraordinary_expenses(responses)


def show_fact_sheet_b(responses, derived):
    """
    If any child lives with both parents, custody is shared, so Fact Sheet B
    is indicated.
    """
    return conditional_logic.determine_shared_custody(responses)


def fact_sheet_b_error(responses, derived):
    questions = ['time_spent_with_you',
                 'time_spent_with_spouse',
                 'your_child_support_paid_b',
                 'your_spouse_child_support_paid_b']
    if derived['show_fact_sheet_b']:
        return _any_question_errors(responses, questions)


def show_fact_sheet_c(responses, derived):
    """
    If any child lives with one parent and there's another child who lives with
    the other parent or is shared, Fact Sheet C is indicated.
    """
    return conditional_logic.determine_split_custody(responses)


def fact_sheet_c_error(responses, derived):
    questions = ['your_spouse_child_support_paid_c', 'your_child_support_paid_c']
    if derived['show_fact_sheet_c']:
        return _any_question_errors(responses, questions)


def show_fact_sheet_d(responses, derived):
    """
    If a claimaint is claiming financial support for a child of the marriage
    over 19, Fact Sheet D is indicated.
    """
    return conditional_logic.determine_child_over_19_supported(responses)


def fact_sheet_d_error(responses, derived):
    questions = [
        'number_children_over_19_need_support',
        'agree_to_guideline_child_support_amount',
        'appropriate_spouse_paid_child_support',
        'suggested_child_support'
    ]
    if derived['show_fact_sheet_d']:
        return _any_question_errors(responses, questions)


def show_fact_sheet_e(responses, derived):
    """
    If the claimant is claiming undue hardship, Fact Sheet E is indicated.
    """

    return responses.get('claiming_undue_hardship', '') == 'YES'


def fact_sheet_e_error(responses, derived):
    return conditional_logic.determine_missing_undue_hardship_reasons(responses)


def show_fact_sheet_f_you(responses, derived):
    return determine_show_fact_sheet_f_you(responses)


def show_fact_sheet_f_spouse(responses, derived):
    return determine_show_fact_sheet_f_spouse(responses)


def show_fact_sheet_f(responses, derived):
    """
    If one of the claimants earns over $150,000, Fact Sheet F is indicated.
    """
    return derived['show_fact_sheet_f_you'] or derived['show_fact_sheet_f_spouse']


def fact_sheet_f_error(responses, derived):
    """
    Helper to see if there are any errors for missing required fields
    """
    fields_for_you = ['number_children_seeking_support_you',
                      'child_support_amount_under_high_income_you',
                      'percent_income_over_high_income_limit_you',
                      'amount_income_over_high_income_limit_you',
                      'agree_to_child_support_amount_you',
                      'agreed_child_support_amount_you',
                      'reason_child_support_amount_you',
                      ]
    fields_for_spouse = ['number_children_seeking_support_spouse',
                         'child_support_amount_under_high_income_spouse',
                         'percent_income_over_high_income_limit_spouse',
                         'amount_income_over_high_income_limit_spouse',
                         'agree_to_child_support_amount_spouse',
                         'agreed_child_support_amount_spouse',
                         'reason_child_support_amount_spouse']
    if show_fact_sheet_f_you(responses, derived):
        if _any_question_errors(responses, fields_for_you):
            return True
    if show_fact_sheet_f_spouse(responses, derived):
        if _any_question_errors(responses, fields_for_spouse):
            return True
    return False


def has_fact_sheets(responses, derived):
    """ Return whether or not the user is submitting fact sheets """
    return any([derived['show_fact_sheet_b'], derived['show_fact_sheet_c'],
                derived['show_fact_sheet_d'], derived['show_fact_sheet_e'],
                derived['show_fact_sheet_f'], ])


def child_support_payor_b(responses, derived):
    """ Return who the payor is depends on the monthly amount from Factsheet B """
    try:
        amount_1 = float(responses.get('your_child_support_paid_b', 0))
    except ValueError:
        amount_1 = 0

    try:
        amount_2 = float(responses.get('your_spouse_child_support_paid_b', 0))
    except ValueError:
        amount_2 = 0

    if amount_1 > amount_2:
        payor = 'you'
    elif amount_1 < amount_2:
        payor = 'spouse'
    else:
        payor = 'both'

    return payor


def child_support_payor_c(responses, derived):
    """ Return who the payor is depends on the monthly amount from Factsheet C """
    try:
        amount_1 = float(responses.get('your_child_support_paid_c', 0))
    except ValueError:
        amount_1 = 0

    try:
        amount_2 = float(responses.get('your_spouse_child_support_paid_c', 0))
    except ValueError:
        amount_2 = 0

    if amount_1 > amount_2:
        payor = 'you'
    elif amount_1 < amount_2:
        payor = 'spouse'
    else:
        payor = 'both'

    return payor


def guideline_amounts_difference_b(responses, derived):
    """
    Return the difference between the guideline amounts to be paid by
    claimant 1 and claimant 2 for Factsheet B
    """

    try:
        amount_1 = float(responses.get('your_child_support_paid_b', 0))
    except ValueError:
        amount_1 = 0

    try:
        amount_2 = float(responses.get('your_spouse_child_support_paid_b', 0))
    except ValueError:
        amount_2 = 0

    return abs(amount_1 - amount_2)


def guideline_amounts_difference_c(responses, derived):
    """
    Return the difference between the guideline amounts to be paid by
    claimant 1 and claimant 2 for Factsheet C
    """

    try:
        amount_1 = float(responses.get('your_child_support_paid_c', 0))
    except ValueError:
        amount_1 = 0

    try:
        amount_2 = float(responses.get('your_spouse_child_support_paid_c', 0))
    except ValueError:
        amount_2 = 0

    return abs(amount_1 - amount_2)


def guideline_amounts_difference_total(responses, derived):
    """
    Return the sum of the guideline amounts B and C
    """

    amount_b = derived['guideline_amounts_difference_b'] if derived['show_fact_sheet_b'] else 0
    amount_c = derived['guideline_amounts_difference_c'] if derived['show_fact_sheet_c'] else 0

    payor_b = derived['child_support_payor_b']
    payor_c = derived['child_support_payor_c']

    if payor_b == payor_c:
        return amount_b + amount_c
    else:
        return abs(amount_b - amount_c)


def schedule_1_amount(responses, derived):
    """ Return the amount as defined in schedule 1 for child support """

    try:
        if derived['show_fact_sheet_b'] or derived['show_fact_sheet_c']:
            return derived['guideline_amounts_difference_total']
        else:
            return float(responses.get('payor_monthly_child_support_amount', 0))
    except ValueError:
        return 0


def child_support_payor(responses, derived):
    """ Return the payor phrased for the affidavit """
    return determine_child_support_payor(responses)


def child_support_payor_by_name(responses, derived):
    """ Return the payor by name"""

    payor = 'the payor'
    support_payor = child_support_payor(responses, derived)
    if support_payor == 'Claimant 1':
        payor = format_utils.you_name(responses, support_payor)
    elif support_payor == 'Claimant 2':
        payor = format_utils.spouse_name(responses, child_support_payor)
    elif support_payor == 'both Claimant 1 and Claimant 2':
        payor = '{} and {}'.format(format_utils.you_name(responses, 'myself'),
                                   format_utils.spouse_name(responses, 'my spouse'))
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


def total_child_support_payment_a(response, derived):
    """ Return the total monthly child support payable by the payor for Fact Sheet A """
    total = 0
    if sole_custody(response, derived):
        total += derived['schedule_1_amount']
    else:
        if derived['show_fact_sheet_b']:
            total += guideline_amounts_difference_b(response, derived)
        if derived['show_fact_sheet_c']:
            total += guideline_amounts_difference_c(response, derived)

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

    difference = derived['guideline_amounts_difference_b']

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


def child_support_acts(responses, derived):
    """ Strip off unnecessary characters from child_support_act value """
    act = responses.get('child_support_act', '').replace('"', '').replace('[', '').replace(']', '').replace(' ,', ' and ')
    return act


def pursuant_parenting_arrangement(responses, derived):
    """
    Return a list of parenting arrangement bullet points, prefaced by the
    correct 'pursuant to' phrase.
    """

    act = derived['child_support_acts']
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

    act = derived['child_support_acts']
    act = 'Pursuant to %s,' % act if act != '' else act
    try:
        arrangements = responses.get('order_for_child_support', '').split('\n')
        return ['%s %s' % (act, arrangement.strip())
                for arrangement in arrangements
                if len(arrangement.strip()) > 0]
    except ValueError:
        return []


def sole_custody(responses, derived):
    """
    Return True if either parent has sole custody of the children
    """
    return conditional_logic.determine_sole_custody(responses)


def number_of_children(responses, derived):
    return conditional_logic.get_num_children_living_with(responses, 'Lives with both')


def number_of_children_claimant(responses, derived):
    return conditional_logic.get_num_children_living_with(responses, 'Lives with you')


def number_of_children_claimant_spouse(responses, derived):
    return conditional_logic.get_num_children_living_with(responses, 'Lives with spouse')


def any_errors(responses, derived):
    for question_key in responses:
        if question_key.endswith('_error'):
            return True
    return False


def _any_question_errors(responses, questions):
    for field in questions:
        error_field_name = f'{field}_error'
        if responses.get(error_field_name):
            return True
    return False
