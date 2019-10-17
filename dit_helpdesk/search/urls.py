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
        "api/commodity-term/",
        views.CommodityTermSearchAPIView.as_view(),
        name="commodity-term-api-search",
    ),
    path(
        "api/commodity-code/",
        views.CommodityCodeSearchAPIView.as_view(),
        name="commodity-code-api-search",
    ),
    path(
        "api/hierarchy/",
        views.HierarchySearchAPIView.as_view(),
        name="hierarchy-api-search",
    ),
]
