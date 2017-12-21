from datetime import datetime
import json

from django import template

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

    tag = ['<input type="{}" value="{:.2f}" step="{}" '.format(input_type, float(value), step)]

    if name != '':
        tag.append('name="{}"'.format(name))

    tag = additional_attributes(tag, **kwargs)
    tag.append('>')
    return ''.join(tag)


@register.simple_tag(takes_context=True)
def input_field(context, type, name='', value='', multiple='', **kwargs):
    """
    Usage:  when specifying data attributes in templates, use "data_" instead of "data-".
    """
    if type == "textarea":
        tag = ['<textarea name="' + name + '"']

        tag = additional_attributes(tag, **kwargs)

        tag.append('>')

        if value == '':
            tag.append(context.get(name, ''))
        else:
            tag.append(value)

        tag.append('</textarea>')
    else:
        # set initial value for textbox
        if type == "text":
            if value == '' and multiple != 'true':
                value = context.get(name, '')
            if 'date-picker' in kwargs.get('class', ''):  # DIV-573
                try:
                    date = datetime.strptime(value, '%d/%m/%Y')
                    value = f'{date:%b} {date.day}, {date:%Y}'
                    if context['request'].user.is_authenticated():
                        UserResponse.objects.filter(
                            bceid_user=context['request'].user, question=name
                        ).update(value=value)
                    else:
                        context['request'].session[name] = value
                except ValueError:
                    pass  # conversion to current format not needed
        elif type == "number":
            value = context.get(name, '')
        tag = ['<input type="%s" name="%s" value="%s"' % (type, name, value)]

        tag = additional_attributes(tag, **kwargs)

        # check if buttons should be selected by default
        if type == 'checkbox':
            value_list = json.loads(context.get(name, '[]'))
        else:
            value_list = context.get(name, '')

        if value_list is not None and value != '' and value in value_list:
            tag.append(' checked')

        tag.append('>')

    return ''.join(tag)


def additional_attributes(tag, **kwargs):
    for key, data_val in kwargs.items():
        if str.startswith(key, 'data_'):
            key = str.replace(key, 'data_', 'data-')
        tag.append(' ' + key + '="' + data_val + '"')
    return tag


@register.assignment_tag
def check_list(source, value):
    """
    Check if given value is in the given source
    """
    try:
        return value in json.loads(source)
    except:
        return False


@register.assignment_tag
def multiple_values_to_list(source):
    try:
        return json.loads(source)
    except:
        return []
