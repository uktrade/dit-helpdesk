from django import template

register = template.Library()


@register.filter(name="replace")
def cell_cleaner(value):
    return value.replace("_", " ")
