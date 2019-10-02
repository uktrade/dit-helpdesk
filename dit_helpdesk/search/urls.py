from django.urls import re_path, path

from search import views

app_name = "search"

urlpatterns = [
    re_path(
        r"country/(?P<country_code>\w+)/$",
        views.CommoditySearchView.as_view(),
        name="search-commodity",
    ),
    re_path(
        r"country/(?P<country_code>\w+)/hierarchy/(?P<node_id>.+)",
        views.search_hierarchy,
        name="search-hierarchy",
    ),
    path(
        "api/commodity/",
        views.CommoditySearchAPIView.as_view(),
        name="commodity-api-search",
    ),
    path(
        "api/hierarchy/",
        views.HierarchySearchAPIView.as_view(),
        name="hierarchy-api-search",
    ),
]
