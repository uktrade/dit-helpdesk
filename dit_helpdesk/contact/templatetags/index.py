from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    print("indexable:", indexable, i)
    return indexable[i]
