"""helpdesk_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

from commodities import views as commodity_views
from countries import views as country_views
from hierarchy import views as hierarchy_views
from search import views as search_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'choose_country/', country_views.choose_country_view,
        name='choose-country'
    ),
    re_path(
        r'commodity/(?P<commodity_code>\d{10})',
        commodity_views.commodity_detail, name='commodity-detail'
    ),
    re_path(
        r'commodity_measures_table/(?P<commodity_code>\d{10})/(?P<origin_country>[a-zA-Z]{2})',
        commodity_views.get_measure_table_data, name='commodity-measures-table'
    ),
    path('search/', search_views.search_view, name='search-view'),
    path('hierarchy/', hierarchy_views.hierarchy, name='hierarchy-view'),
    path('hierarchy_data/', hierarchy_views.get_hierarchy_data),
    path('hierarchy_data_cached/', hierarchy_views.get_hierarchy_data_cached),
]

'''
urlpatterns = [
    path('admin/', admin.site.urls),
    path('commodities/', views.commodity_list, name='commodity_list'),
    
    #re_path(r'^search/', include('haystack.urls')),
    re_path(r'^search*?', CommoditySearchView.as_view(), name='commodity-search-view'),

    

    re_path(r'section_data/(?P<section_id>\d+)', views.get_section_data),

    
    path(
        r'choose_country/', views.choose_country_view, name='choose-country'
    ),
    # path(
    #     r'search/', views.search_commodities_view, name='search-commodities'
    # ),

    re_path(
        r'headings/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_detail, name='heading-detail'
    ),
    re_path(
        r'heading_data/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_data, name='heading-data'
    ),
]
'''