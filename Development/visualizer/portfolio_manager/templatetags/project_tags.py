from django import template

register = template.Library()

@register.filter
def get(dict, key):
    try:
        return dict[key]
    except KeyError:
        return None
