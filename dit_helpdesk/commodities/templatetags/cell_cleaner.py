# import re
# from datetime import datetime
# from django.utils.dateparse import parse_datetime
from django import template

register = template.Library()

@register.filter
def cell_cleaner(value):

  # match = re.match('\d\d\d\d-\d\d\-\d\d', value)

  if value == '':
    return '-'
  # elif match != None:
  #   date = datetime.strptime(value, '%Y-%m-%d')
  #   return f'{date.day} {date:%B} {date.year}'
  else:
    return value.replace(' %','%').replace('VAT', '<abbr title="Value Added Tax">VAT</abbr>')
