from django.urls import re_path

from search import views
from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

app_name = 'search'

router = SimpleRouter()
router.register(
    prefix=r'',
    basename='search',
    viewset=views.CommodityViewSet
)

urlpatterns = [
    re_path(r'^api/', include(router.urls)),
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

