from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commodities.models import Commodity
from countries.models import Country

from hierarchy.views import hierarchy_data
from hierarchy.models import Chapter, Heading, SubHeading


def search_hierarchy(request, node_id='root', country_code=None):
    if country_code is None:
        country_code = request.session.get('origin_country')

    context = {
        'hierarchy_html': hierarchy_data(country_code, node_id),
        'country_code': country_code
    }

    return render(request, 'search/commodity_search.html', context)


def search_view(request, country_code=None):
    if country_code is None:
        if 'country' in request.GET:
            country_code = request.GET['country']
        else:
            return redirect(reverse('choose-country'))

    countries = Country.objects.all()

    if 'q' not in request.GET:
        context = {
            'hierarchy_html': hierarchy_data(country_code),
            'country_code' : country_code
        }

        return render(request, 'search/commodity_search.html', context)

    query = request.GET['q'].strip()


    # SEARCH PRE-PROCESSING:
    # deal with 1 digits, e.g., convert 2 to 02
    if len(query) == 1:
        query = '0' + query

    # deal with illegal 3,5,7,9 digit codes by removing final digit
    if len(query) in [3,5,7,9]:
    	query = query[:-1]

    # deal with false positives 00 & 99
    if query in ['00', '99']:
        query = '9999'

    # A heading ending with two zeroes is a chapter hence remove last 2 digits
    if len(query) == 4 and query[2:] == '00':
        query = query[:2]

    # 
    if len(query) == 8:
        query = query + '00'


    if len(query) == 10 and query.isdigit():
        code = query

        if Commodity.objects.filter(commodity_code=code).exists():
            return redirect(reverse(
                'commodity-detail', kwargs={'commodity_code':code,
                                            'country_code': country_code.lower() }
            ))
        else:


            kwargs = {
                'country_code': country_code.lower()
            }
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search', kwargs=kwargs))


    elif len(query) == 2 and query.isdigit():
        code2 = query
        code2_10 = code2 + '00000000'

        if Chapter.objects.filter(chapter_code=code2_10).exists():

            kwargs = {
                'node_id': 'chapter-%s' % Chapter.objects.get(chapter_code=code2_10).id,
                'country_code': country_code.lower()
            }
            return redirect(reverse('search-hierarchy', kwargs=kwargs))

        else:

            kwargs = {
                'country_code': country_code.lower()
            }
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search', kwargs=kwargs))    


    elif len(query) == 4 and query.isdigit():
        code4 = query
        code4_10 = code4 + '000000'

        if Heading.objects.filter(heading_code=code4_10).exists():

            kwargs = { 
                'node_id': 'heading-%s' % Heading.objects.get(heading_code=code4_10).id,
                'country_code': country_code.lower()
            }   
            return redirect(reverse('search-hierarchy', kwargs=kwargs))

        else:
            kwargs = {
                'country_code': country_code.lower()
            }
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search', kwargs=kwargs))


    elif len(query) == 6 and query.isdigit():
        code6 = query
        code6_10 = code6 + '0000'

        if SubHeading.objects.filter(commodity_code=code6_10).exists():

            kwargs = {
                'node_id': 'sub_heading-%s' % SubHeading.objects.filter(commodity_code=code6_10).first().id,
                'country_code': country_code.lower()
            }
            return redirect(reverse('search-hierarchy', kwargs=kwargs))

        else:
            kwargs = {
                'country_code': country_code.lower()
            }
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search', kwargs=kwargs))


    else:
        #print('else')
        #messages.error('Expected 10-digit code')
        # return redirect(reverse('search-view'))
        kwargs = { 
            'country_code': country_code.lower()
        }   

        return redirect(reverse('search', kwargs=kwargs))


    return render(request, 'countries/choose_country.html', context)




