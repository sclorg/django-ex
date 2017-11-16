"""
    Mapping between question step names and the numerical values assigned
    to their templates
"""
template_step_order = {
    'orders': 1,
    'claimant': 2,
    'respondent': 3,
    'marriage': 4,
    'separation': 5,
    'children': 6,
    'support': 7,
    'property': 8,
    'other_orders': 9,
    'other_questions': 10,
    'location': 11,
    'fact_sheets': 12,
    'review': 13
}


def get_step_name(step_order):
    """
    Preforms a reverse lookup in the template_step_order dictionary
    """
    return next(k for k, v in template_step_order.items() if v == step_order)


