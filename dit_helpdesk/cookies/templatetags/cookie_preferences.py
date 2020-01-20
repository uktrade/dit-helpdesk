from . import register
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template import loader

@register.inclusion_tag("banner.html")
def cookie_banner():
    return {}
