from django import template

register = template.Library()


@register.filter(name='replace')
def cell_cleaner(value):

    if value == '':
        return ''
    else:
        return value.replace('_', ' ')
