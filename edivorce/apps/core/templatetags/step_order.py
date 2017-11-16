from django import template
import json
from ..utils.template_step_order import template_step_order, get_step_name

register = template.Library()


@register.simple_tag(takes_context=True)
def step_order(context, step):
    want_which_orders = __parse_json_which_orders_selected(context)
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
def next_step(context, step):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    current_step_base_order = template_step_order[step]

    next_item = current_step_base_order + 1

    if next_item == 6 and 'Spousal support' not in want_which_orders:
        next_item += 1

    if next_item == 7 and 'Division of property and debts' not in want_which_orders:
        next_item += 1

    if next_item == 8 and 'Other orders' not in want_which_orders:
        next_item += 1

    return get_step_name(next_item)


@register.simple_tag(takes_context=True)
def prev_step(context, step):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    current_step_base_order = template_step_order[step]

    prev = current_step_base_order - 1

    if prev == 8 and 'Other orders' not in want_which_orders:
        prev -= 1

    if prev == 7 and 'Division of property and debts' not in want_which_orders:
        prev -= 1

    if prev == 6 and 'Spousal support' not in want_which_orders:
        prev -= 1

    return get_step_name(prev)


def __parse_json_which_orders_selected(context):
    """
    Get the list of orders requested by the users on step 1.
    This determies which steps will be hidden.
    """
    # for regular question pages, the value we want is stored in 'want_which_orders'
    want_which_orders = context.get('want_which_orders', None)
    if want_which_orders is None:

        # for the review page, responses are nested in a special format
        which_orders = context.get('which_orders', None)

        if which_orders is not None and len(which_orders) >= 1:
            want_which_orders = which_orders[0]["value"]
    if want_which_orders is None:
        want_which_orders = json.loads('[]')
    else:
        want_which_orders = json.loads(want_which_orders)
    return want_which_orders