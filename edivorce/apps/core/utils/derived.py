# pylint: disable=W0613
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
    'schedule_1_payor',
    'fact_sheet_a_total',
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
        annual = int(responses.get('annual_gross_income', 0))
    except ValueError:
        annual = 0

    try:
        spouses = int(responses.get('spouse_annual_gross_income', 0))
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

    return 155689.333


def schedule_1_payor(responses, derived):
    """ Return the amount as defined in schedule 1 for child support """

    return 'Claimant 1'


def fact_sheet_a_total(responses, derived):
    """ Return the total amount of special expenses from Fact Sheet A """

    return 0



