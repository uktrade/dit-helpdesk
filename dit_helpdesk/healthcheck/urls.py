from django.urls import path

from healthcheck import views

app_name = "healthcheck"

urlpatterns = [
    path("", views.HealthCheckView.as_view(), name="basic"),
    path("tree_freshness", views.TreeRefreshCheckView.as_view(), name="tree_freshness"),
    path("cms_existence", views.CMSCheckView.as_view(), name="cms_existence"),
]
