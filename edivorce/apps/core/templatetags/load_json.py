import json

from django import template

register = template.Library()

@register.filter
def load_json(data):
    return json.loads(data)