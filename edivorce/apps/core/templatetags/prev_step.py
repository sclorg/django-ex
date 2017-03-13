from django import template
import json
from ..utils.template_step_order import template_step_order, get_step_name

register = template.Library()


@register.simple_tag(takes_context=True)
def step_order(context, step):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    base_order = template_step_order[step]
    order = base_order

    if base_order > 6 and 'Spousal support' not in want_which_orders:
        order -= 1

    if base_order > 7 and 'Division of property and debts' not in want_which_orders:
        order -= 1

    if base_order > 8 and 'Other orders' not in want_which_orders:
        order -= 1

    return order


@register.simple_tag(takes_context=True)
def prev_step(context, step):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    current_step_base_order = template_step_order[step]

    prev = current_step_base_order - 1

    if current_step_base_order > 6 and 'Spousal support' not in want_which_orders:
        prev -= 1

    if current_step_base_order > 7 and 'Division of property and debts' not in want_which_orders:
        prev -= 1

    if current_step_base_order > 8 and 'Other orders' not in want_which_orders:
        prev -= 1

    return get_step_name(prev)
