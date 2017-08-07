from django import template

register = template.Library()

@register.filter
def get(dict, key):
    try:
        return dict[key]
    except KeyError:
        return None

@register.filter
def get_or_empty(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''

@register.filter
def ct_name(ct):
    return ct.name.replace(' dimension', '').capitalize()


@register.filter
def get_type(ct):
    return ct.name.replace(' ', '').replace('dimension', '')


@register.filter
def is_type(dim_type, input_type):
    value_types = ['text', 'number', 'date']
    dropdown_types = ['associatedperson', 'associatedorganization']
    multiple_types = ['associatedpersons', 'associatedprojects']

    if input_type == 'value':
        return dim_type in value_types
    elif input_type == 'dropdown':
        return dim_type in dropdown_types
    elif input_type == 'multiple':
        return dim_type in multiple_types
    else:
        return False


@register.filter
def get_valuetype(dim_type):
    if is_type(dim_type, 'value'):
        return 'value'
    elif is_type(dim_type, 'dropdown'):
        return 'dropdown'
    elif is_type(dim_type, 'multiple'):
        return 'multiple'
    else:
        return 'None'

@register.filter
def add_form_control(input):
    input.field.widget.attrs['class'] = 'form-control'
    return input
