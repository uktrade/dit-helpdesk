from django import template

register = template.Library()


@register.filter(name="cell_cleaner")
def cell_cleaner(value):

    if value == "":
        return "-"
    else:
        return value.replace(" %", "%").replace(
            "VAT", '<abbr title="Value Added Tax">VAT</abbr>'
        )
