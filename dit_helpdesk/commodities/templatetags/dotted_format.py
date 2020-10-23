import re

from django import template

register = template.Library()


@register.filter(name="dotted_format")
def dotted_format(value):
    pattern = r"^([0-9]{4})([0-9]{2})?([0-9]{2})?([0-9]{2})?"
    matched = re.match(pattern, value).groups()

    return ".".join(m for m in matched if m)
