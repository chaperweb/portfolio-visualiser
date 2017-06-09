from django import template

register = template.Library()

@register.filter
def get(dict, key):
    try:
        return dict[key]
    except KeyError:
        return None

@register.filter
def ct_name(ct):
    return ct.name.replace(' dimension', '').capitalize()


@register.filter
def get_type(ct):
    return ct.name.replace(' ', '').replace('dimension', '')
