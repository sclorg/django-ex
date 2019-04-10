"""
Template tags that output composite results based on context that includes the
users full responses.
"""
from django import template

from .format_utils import date_formatter, money
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def effective_date(context):
    """ Returns the effective date of the divorce, based on user's answers """

    effective = 'the 31st day after the date of this order'
    if context['responses'].get('divorce_take_effect_on', '') == 'specific date':
        date = context['responses'].get('divorce_take_effect_on_specific_date', '')
        if date == '':
            effective = format_html('<span class="form-entry not-complete"></span>')
        else:
            effective = date_formatter(date)
    return effective


@register.simple_tag(takes_context=True)
def monthly_child_support_amount(context):
    """ Returns monthly child support amount based on user's answers """

    amount = '0.00'
    if context['responses'].get('child_support_in_order', '') == 'DIFF':
        amount = context['responses'].get('order_monthly_child_support_amount', '')
    elif context['responses'].get('child_support_in_order', '') == 'MATCH':
        if context['derived'].get('show_fact_sheet_b', '') or context['derived'].get('show_fact_sheet_c', ''):
            """ Shared or Split custody """
            amount = context['responses'].get('difference_payment_amounts', '')
        else:
            """ Sole custody """
            amount = context['derived'].get('schedule_1_amount', '')

    return money(amount)
