from django import template
import json

from django.urls import reverse

from ..utils.template_step_order import template_step_order, template_sub_step_order, get_step_name, \
    get_step_or_sub_step_name

register = template.Library()


def _get_next_step(context, step, sub_step, direction):
    want_which_orders = json.loads(context.get('want_which_orders', '[]'))
    children_of_marriage = context.get('derived', {}).get('has_children_of_marriage')
    sub_step_name = _get_next_sub_step(step, sub_step, want_which_orders,
                                       children_of_marriage=children_of_marriage,
                                       direction=direction)
    if sub_step_name is not None:
        return sub_step_name

    current_step_base_order = template_step_order[step]
    next_item = _adjust_for_orders(current_step_base_order, want_which_orders,
                                   children_of_marriage=children_of_marriage,
                                   direction=direction)

    # The next page or previous page could land on a sub step page so need to do lookup to find
    # out where may fall.
    return get_step_or_sub_step_name(next_item, direction=direction)


def _get_next_sub_step(step, sub_step, want_which_orders, children_of_marriage, direction):
    current_step_base_order = template_step_order[step]
    if template_sub_step_order.get(step, None) is not None:
        current_sub_step_base_order = template_sub_step_order[step].get(sub_step, None)
        if current_sub_step_base_order is not None:
            if direction == 'next':
                next_item = current_sub_step_base_order + 1
            else:
                next_item = current_sub_step_base_order - 1
            next_sub_step = get_step_name(template_sub_step_order[step], next_item)
            if next_sub_step is not None:
                return reverse('question_steps', kwargs={'step': step, 'sub_step': next_sub_step})

        next_item = _adjust_for_orders(current_step_base_order, want_which_orders,
                                       children_of_marriage=children_of_marriage,
                                       direction=direction)
        return reverse('question_steps', kwargs={'step': get_step_name(template_step_order, next_item)})
    return None


def _adjust_for_orders(next_item, want_which_orders, children_of_marriage, direction):
    print(children_of_marriage)
    tests = [
        lambda next_item: next_item == 6 and not children_of_marriage,
        lambda next_item: next_item == 7 and 'Spousal support' not in want_which_orders,
        lambda next_item: next_item == 8 and 'Division of property and debts' not in want_which_orders,
        lambda next_item: next_item == 9 and 'Other orders' not in want_which_orders
    ]
    addend = 1
    if direction != 'next':
        addend = -1
        tests.reverse()
    next_item += addend

    for test in tests:
        if test(next_item):
            next_item += addend
    return next_item


@register.simple_tag(takes_context=True)
def step_order(context, step):
    base_order = template_step_order[step]
    order = base_order
    derived_data = context.get('derived', dict())

    if base_order > 5 and not derived_data.get('has_children_of_marriage'):
        order -= 1

    if base_order > 6 and not derived_data.get('wants_spousal_support'):
        order -= 1

    if base_order > 7 and not derived_data.get('wants_property_division'):
        order -= 1

    if base_order > 8 and not derived_data.get('wants_other_orders'):
        order -= 1

    return order


@register.simple_tag(takes_context=True)
def next_step(context, step, sub_step=None):
    return _get_next_step(context, step, sub_step, 'next')


@register.simple_tag(takes_context=True)
def prev_step(context, step, sub_step=None):
    return _get_next_step(context, step, sub_step, 'previous')


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
