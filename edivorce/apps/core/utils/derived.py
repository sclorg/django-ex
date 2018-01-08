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

DERIVED = [
    'show_fact_sheet_a',
    'show_fact_sheet_b',
    'show_fact_sheet_c',
    'show_fact_sheet_d',
    'show_fact_sheet_e',
    'show_fact_sheet_f',
]


def get_derived_data(responses):
    """ Return a dict of data derived from the user's responses """

    functions = globals()
    return {func: functions[func](responses) for func in DERIVED}


def show_fact_sheet_a(responses):
    """
    If the claimant is claiming special extraordinary expenses, Fact Sheet A is
    indicated.
    """

    expenses = json.loads(responses.get('special_extraordinary_expenses', '[]'))
    return len(expenses) > 0 and "None" not in expenses


def show_fact_sheet_b(responses):
    """
    If any child lives with both parents, custody is shared, so Fact Sheet B
    is indicated.
    """

    children = json.loads(responses.get('claimant_children', '[]'))
    print(children)
    return any([child['child_live_with'] == 'Lives with both'
                for child in children])


def show_fact_sheet_c(responses):
    """
    If any child lives with one parent and there's another child who lives with
    the other parent or is shared, Fact Sheet C is indicated.
    """

    with_you = 0
    with_spouse = 0
    with_both = 0
    children = json.loads(responses.get('claimant_children', '[]'))
    for child in children:
        if child['child_live_with'] == 'Lives with you':
            with_you += 1
        elif child['child_live_with'] == 'Lives with spouse':
            with_spouse += 1
        elif child['child_live_with'] == 'Lives with both':
            with_both += 1
    return (with_you > 0 and (with_spouse + with_both > 0) or
            with_spouse > 0 and (with_you + with_both > 0))


def show_fact_sheet_d(responses):
    """
    If a claimaint is claiming financial support for a child of the marriage
    over 19, Fact Sheet D is indicated.
    """

    support = json.loads(responses.get('children_financial_support', '[]'))
    return len(support) > 0 and "NO" not in support


def show_fact_sheet_e(responses):
    """
    If the claimant is claiming undue hardship, Fact Sheet E is indicated.
    """

    return responses.get('claiming_undue_hardship', '') == 'YES'


def show_fact_sheet_f(responses):
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
