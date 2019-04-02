import re
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django import template

register = template.Library()

@register.filter
def cell_cleaner(value):


  if value == '':
    return '-'
  else:
    return value.replace(' %','%').replace('VAT', '<abbr title="Value Added Tax">VAT</abbr>')
