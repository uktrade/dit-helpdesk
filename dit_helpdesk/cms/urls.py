from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("", views.CMSView.as_view(), name="home"),
    path("regulation-groups/", views.RegulationGroupsListView.as_view(), name="regulation-groups-list"),
]
