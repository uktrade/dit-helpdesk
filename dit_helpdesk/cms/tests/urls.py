from django.urls import path

from .test_base_cms_mixin import MyView

urlpatterns = [
    path("test-base-cms-mixin", MyView.as_view(), name="test-base-cms-mixin"),
]
