from django.shortcuts import render

def error404handler(request, *args, **argv):
  response = render(request, 'core/404.html')
  response.status_code = 404

  return response

def error500handler(request, *args, **argv):
  response = render(request, 'core/500.html')
  response.status_code = 500

  return response
