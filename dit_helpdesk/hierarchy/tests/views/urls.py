from django.urls import re_path

from config.urls import urlpatterns as base_urlpatterns

from .test_base import TestBaseCommodityObjectDetailView


test_urlpatterns = [
    re_path(
        r"test-base-commodity-object-detail-view/(?P<country_code>\w+)/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)/$",
        TestBaseCommodityObjectDetailView.as_view(),
        name="test-base-commodity-object-detail-view",
    ),
]

urlpatterns = base_urlpatterns + test_urlpatterns
