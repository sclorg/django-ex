from django import template
from datetime import datetime
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linebreaksul(value):
    "Converts strings with newlines into <ul><li></li></ul>s"
    value = re.sub(r'\r\n|\r|\n', '\n', value.strip())  # normalize newlines
    lines = re.split('\n', value)
    lines = ['<li>%s</li>' % line for line in lines if line and not line.isspace()]
    return mark_safe('<ul>%s</ul>' % '\n'.join(lines))


@register.filter
def date_formatter(value):
    """
        Changes date format from dd/mm/yyyy to dd/mmm/yyyy
    """
    d = datetime.strptime(value, '%d/%m/%Y')
    return d.strftime('%d %b %Y')

