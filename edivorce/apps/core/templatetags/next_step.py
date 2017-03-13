from django import template
import json
from ..utils.template_step_order import template_step_order, get_step_name

register = template.Library()


@register.simple_tag(takes_context=True)
def next_step(context, step):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    current_step_base_order = template_step_order[step]

    next = current_step_base_order + 1

    if current_step_base_order == 5 and 'Spousal support' not in want_which_orders:
        next += 1

    if next == 6 and 'Division of property and debts' not in want_which_orders:
        next += 1

    if next == 7 and 'Other orders' not in want_which_orders:
        next += 1

    return get_step_name(next)



