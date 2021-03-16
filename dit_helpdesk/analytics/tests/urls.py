from django.urls import path

from .test_middleware import TestMiddlewareView

urlpatterns = [
    path("test-middleware", TestMiddlewareView.as_view(), name="test-middleware"),
]
