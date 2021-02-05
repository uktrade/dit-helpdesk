from django import template

register = template.Library()


@register.filter(name="replace")
def cell_cleaner(value):

    return value.replace("_", " ")


@register.filter(name="blank_none")
def blank_none(value):
    if value is None:
        return ''
    return value


@register.filter(name="set_country")
def set_country(value, country_code):
    if not value:
        return ''

    return value.format(country_code=country_code)
