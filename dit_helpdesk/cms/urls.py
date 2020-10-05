from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("", views.CMSView.as_view(), name="home"),
    path("regulation-groups/", views.RegulationGroupsListView.as_view(), name="regulation-groups-list"),
    path("regulation-group/<int:pk>/", views.RegulationGroupDetailView.as_view(), name="regulation-group-detail"),
    path(
        "regulation-group/<int:pk>/regulation/create/",
        views.RegulationGroupRegulationCreateView.as_view(),
        name="regulation-group-regulation-create",
    ),
    path(
        "regulation-group/<int:pk>/chapters/",
        views.RegulationGroupChapterListView.as_view(),
        name="regulation-group-chapter-list",
    ),
    path(
        "regulation-group/<int:pk>/chapters/add/",
        views.RegulationGroupChapterAddView.as_view(),
        name="regulation-group-chapter-add",
    )
]
