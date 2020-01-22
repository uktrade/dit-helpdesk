from . import register
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template import loader


def render_gtm_template(template_filename):
    t = loader.get_template(template_filename)

    return t.render({
        'HELPDESK_GA_GTM': settings.HELPDESK_GA_GTM
    })


@register.simple_tag()
def google_tag_manager():
    if not settings.HELPDESK_GA_GTM:
        return mark_safe("<!-- missing GTM container id -->")

    return render_gtm_template("gtm.html")


@register.simple_tag()
def google_tag_manager_noscript():
    if not settings.HELPDESK_GA_GTM:
        return mark_safe("<!-- missing GTM container id -->")

    return render_gtm_template("gtm_noscript.html")
