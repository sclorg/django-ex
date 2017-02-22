from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def input_field(context, type, name='', value='', **kwargs):
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
        if type == "text":
            value = context.get(name, '')
        tag = ['<input type="' + type + '" name="' + name + '" value="' + value + '"']

        tag = additional_attributes(tag, **kwargs)

        # check if buttons should be selected by default
        value_list = context.get(name, '').split('; ')

        if value in value_list and value != '':
            tag.append(' checked')

        tag.append('>')

    return ''.join(tag)


def additional_attributes(tag, **kwargs):
    for key, data_val in kwargs.items():
        if str.startswith(key, 'data_'):
            key = str.replace(key, 'data_', 'data-')
        tag.append(' ' + key + '="' + data_val + '"')
    return tag
