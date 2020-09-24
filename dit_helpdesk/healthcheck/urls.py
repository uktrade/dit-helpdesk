from django.urls import path

from healthcheck import views

app_name = "healthcheck"

urlpatterns = [

    path('', views.HealthCheckView.as_view(), name="basic"),
    path('tree_freshness', views.TreeRefreshCheckView.as_view(), name="tree_freshness")
]
