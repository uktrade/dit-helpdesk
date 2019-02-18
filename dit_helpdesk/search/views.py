from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commodities.models import Commodity


@login_required
def search_view(request):

    if 'q'not in request.GET:
        return render(request, 'search/commodity_search.html', {})

    query = request.GET['q'].strip()
    if len(query) == 10 and query.isdigit():
        code = query
        if Commodity.objects.filter(commodity_code=code).exists():
            return redirect(reverse(
                'commodity-detail', kwargs={'commodity_code':code}
            ))
        else:
            messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search-view'))
    else:
        messages.error('Expected 10-digit code')
        return redirect(reverse('search-view'))

