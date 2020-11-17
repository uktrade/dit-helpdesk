from django.urls import path

from .test_helpers import MyView


urlpatterns = [
    path("test-require-feature", MyView.as_view(), name="test-require-feature"),
]
