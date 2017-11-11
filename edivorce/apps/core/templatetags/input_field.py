from django import template
import json

register = template.Library()


@register.simple_tag(takes_context=True)
def input_field(context, type, name='', value='', multiple='', **kwargs):
    """
    Usage:  when specifying data attributes in templates, use "data_" intead of "data-".
    """
    if type == "textarea":
        tag = ['<textarea name="' + name + '"']

        tag = additional_attributes(tag, **kwargs)

        tag.append('>')

        tag.append(context.get(name, ''))

        tag.append('</textarea>')
    else:
        # set initial value for textbox
        if type == "text" and value == '' and multiple != 'true':
            value = context.get(name, '')
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
