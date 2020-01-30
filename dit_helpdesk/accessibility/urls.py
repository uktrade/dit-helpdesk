from django.urls import re_path

from accessibility import views

app_name = "accessibility"

urlpatterns = [

    re_path(
        "",
        views.AccessibilityView.as_view(),
        name="accessibility",
    ),
]
