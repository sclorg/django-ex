from django import template
from datetime import datetime
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linebreaksli(value):
    "Converts strings with newlines into <li></li>s"
    value = re.sub(r'\r\n|\r|\n', '\n', value.strip())  # normalize newlines
    lines = re.split('\n', value)
    lines = ['<li>%s</li>' % line for line in lines if line and not line.isspace()]
    return mark_safe('\n'.join(lines))


@register.filter
def date_formatter(value):
    """
        Changes date format from dd/mm/yyyy to dd/mmm/yyyy
    """

    if value is None or value == '':
        return ''

    try:
        d = datetime.strptime(value, '%d/%m/%Y')
    except ValueError:
        d = None

    if d is None:
        d = datetime.strptime(value, '%b %d, %Y')

    return d.strftime('%d %b %Y')


@register.simple_tag()
def response(field, size=None, trail='', as_date=False):
    """ Return the required field value or the not-entered span """

    if field.strip():
        return '%s%s' % (date_formatter(field) if as_date else field, trail)
    style = ('min-width: %spx' % size) if size is not None else ''
    return '<span class="form-entry not-complete" style="%s"></span>' % style


@register.simple_tag()
def required(field, size=None, trail=''):
    """ Return the required field value or the not-entered span """
    return response(field, size, trail)


@register.simple_tag(takes_context=True)
def checkbox(context, *args, **kwargs):
    """
    Return a checkbox icon, checked if all args true.

    Standalone arguments are evaluated as booleans according to normal python
    rules for truthy values.  A boolean is itself; an empty string is False
    while a non-empty string is True; etc.

    Keyword arguments are treated as the key being a question key in the
    responses dict, and the value as a matching value with the response.  If the
    response is a list, the value matches if its in the list.

    The weakness of this tag is that it can't handle negation (e.g., a response
    doesn't equal a particular value).  I don't have a clever way to handle that
    here that doesn't involve adding syntax or unconventional usage (e.g.,
    '^value' means not value).

    NOTE: using the tag with no arguments will result in a checked box since
    all() evaluates empty lists to True.  To simply print an empty checkbox,
    pass a False value as an argument.
    """
    args_pass = all(args)
    kwargs_pass = all([value in context['responses'].get(question, '')
                       for question, value in kwargs.items()])

    return mark_safe('<i class="fa fa%s-square-o" aria-hidden="true"></i>' %
                     ('-check' if args_pass and kwargs_pass else ''))

