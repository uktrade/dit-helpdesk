from django import template

register = template.Library()

@register.filter
def the_world(value):
  if value == 'ERGA OMNES':
    return 'The world'
  else:
    return value