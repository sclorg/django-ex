from datetime import datetime
import json

from django import template
from django.utils.html import format_html

from ..models import UserResponse

register = template.Library()


@register.simple_tag(takes_context=True)
def money_input_field(context, input_type='number', name='', value_src=None, value='', scale_factor=None, **kwargs):
    """

    :param context:
    :param input_type:
    :param name:
    :param value_src:
    :param value:
    :param scale_factor:
    :param kwargs:
    :return:
    """
    if value == '':
        if value_src is None:
            value = context.get(name, 0.0)
        else:
            value = context.get(value_src, 0.0)

    value = value if value != '' else 0.0

    if scale_factor:
        value = float(value) * float(scale_factor)

    step = '0.01'
    if kwargs.get('step', None):
        step = kwargs.get('step')

    tag = format_html(
            '<input type="{}" value="{}" step="{}" min="0"',
            input_type,
            "{:.2f}".format(float(value)),
            step)

    if name != '':
        tag = format_html(
                '{} name="{}"',
                tag,
                name)

    attributes = additional_attributes(**kwargs)
    tag = format_html(
            '{}{} />',
            tag,
            attributes)

    return tag


@register.simple_tag(takes_context=True)
def input_field(context, type, name='', value='', multiple='', **kwargs):
    """
    Usage:  when specifying data attributes in templates, use "data_" instead of "data-".
    """
    error = context.get(f'{name}_error', False)
    if error:
        if 'class' in kwargs:
            kwargs['class'] += ' error'
        else:
            kwargs['class'] = 'error'

    if type == "textarea":
        attributes = additional_attributes(**kwargs)
        if value == '':
            value = context.get(name, '')
        tag = format_html(
            '<textarea name="{}"{}>{}</textarea>',
            name,
            attributes,
            value)
    else:
        # set initial value for textbox
        if type == "text":
            if value == '' and multiple != 'true':
                value = context.get(name, '')
            if 'date-picker' in kwargs.get('class', ''):  # DIV-573
                try:
                    date = datetime.strptime(value, '%d/%m/%Y')
                    value = date.strftime('%b %d, %Y')
                    if context['request'].user.is_authenticated:
                        UserResponse.objects.filter(
                            bceid_user=context['request'].user, question=name
                        ).update(value=value)
                    else:
                        context['request'].session[name] = value
                except ValueError:
                    pass  # conversion to current format not needed
        elif type == "number":
            if value == '':
                value = context.get(name, '')
            elif value.isdigit():
                value = value
            else:
                value = context.get(value, '')

        attributes = additional_attributes(**kwargs)

        # check if buttons should be selected by default
        checked = ''
        if type == 'checkbox':
            value_list = json.loads(context.get(name, '[]'))
        else:
            value_list = context.get(name, '')

        if value_list is not None and value != '' and value in value_list:
            checked = 'checked'

        tag = format_html(
            '<input type="{}" name="{}" value="{}"{} {}/>',
            type,
            name,
            value,
            attributes,
            checked)

    return tag


def additional_attributes(**kwargs):
    attributes = ''
    for key, data_val in kwargs.items():
        if str.startswith(key, 'data_'):
            key = str.replace(key, 'data_', 'data-')
        attributes = format_html(
            '{} {}="{}"',
            attributes,
            key,
            data_val)
    return attributes


@register.simple_tag
def check_list(source, value):
    """
    Check if given value is in the given source
    """
    try:
        return value in json.loads(source)
    except:
        return False


@register.simple_tag
def multiple_values_to_list(source):
    try:
        return json.loads(source)
    except:
        return []
