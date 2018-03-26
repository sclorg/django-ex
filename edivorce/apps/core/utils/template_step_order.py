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
    'review': 12
}

template_sub_step_order = {
    'children': {
        'your_children': 1,
        'income_expenses': 2,
        'facts': 3,
        'payor_medical': 4,
        'what_for': 5
    }
}


def get_step_name(step_order_mappings, step_order):
    """
    Preforms a reverse lookup in the template_step_order or template_sub_step_order dictionary
    depending on which is passed as an argument.
    """
    return next((k for k, v in step_order_mappings.items() if v == step_order), None)


def get_step_or_sub_step_name(step_order, direction='next'):
    next_step = next(k for k, v in template_step_order.items() if v == step_order)
    if next_step in template_sub_step_order:
        sub_step_order = 1
        if direction != 'next':
            sub_step_order = len(template_sub_step_order[next_step].keys())
        next_sub_step = next(k for k, v in template_sub_step_order[next_step].items() if v == sub_step_order)
        return '{}/{}/'.format(next_step, next_sub_step)
    return next_step
