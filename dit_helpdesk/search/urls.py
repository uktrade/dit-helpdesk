from django.urls import re_path

from search import views

app_name = 'search'

urlpatterns = [

    re_path(
        r'country/(?P<country_code>\w+)/$',
        views.CommoditySearchView.as_view(),
        name='search-commodity'
    ),

    re_path(
        r'country/(?P<country_code>\w+)/hierarchy/(?P<node_id>.+)',
        views.search_hierarchy,
        name='search-hierarchy'
    ),

]