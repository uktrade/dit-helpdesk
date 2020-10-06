from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("", views.CMSView.as_view(), name="home"),
    path("regulation-groups/", views.RegulationGroupsListView.as_view(), name="regulation-groups-list"),
    path("regulation-group/create/", views.RegulationGroupCreateView.as_view(), name="regulation-group-create"),
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
    ),
    path(
        "regulation-group/<int:pk>/chapter/<int:chapter_pk>/remove/",
        views.RegulationGroupChapterRemoveView.as_view(),
        name="regulation-group-chapter-remove",
    ),
    path(
        "regulation-group/<int:pk>/headings/",
        views.RegulationGroupHeadingListView.as_view(),
        name="regulation-group-heading-list",
    ),
    path(
        "regulation-group/<int:pk>/headings/add/",
        views.RegulationGroupHeadingAddView.as_view(),
        name="regulation-group-heading-add",
    ),
    path(
        "regulation-group/<int:pk>/heading/<int:heading_pk>/remove/",
        views.RegulationGroupHeadingRemoveView.as_view(),
        name="regulation-group-heading-remove",
    ),
    path(
        "regulation-group/<int:pk>/subheadings/",
        views.RegulationGroupSubHeadingListView.as_view(),
        name="regulation-group-subheading-list",
    ),
    path(
        "regulation-group/<int:pk>/subheadings/add/",
        views.RegulationGroupSubHeadingAddView.as_view(),
        name="regulation-group-subheading-add",
    ),
    path(
        "regulation-group/<int:pk>/subheading/<int:subheading_pk>/remove/",
        views.RegulationGroupSubHeadingRemoveView.as_view(),
        name="regulation-group-subheading-remove",
    ),
    path(
        "regulation-group/<int:pk>/commodities/",
        views.RegulationGroupCommodityListView.as_view(),
        name="regulation-group-commodity-list",
    ),
    path(
        "regulation-group/<int:pk>/commodities/add/",
        views.RegulationGroupCommodityAddView.as_view(),
        name="regulation-group-commodity-add",
    ),
    path(
        "regulation-group/<int:pk>/commodity/<int:commodity_pk>/remove/",
        views.RegulationGroupCommodityRemoveView.as_view(),
        name="regulation-group-commodity-remove",
    ),
]
