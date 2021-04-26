from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(name="urlparams")
def urlparams(*args, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        return "?{}".format(urlencode(safe_args))
    return ""
