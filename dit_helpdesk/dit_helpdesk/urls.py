"""helpdesk_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

from commodities import views as commodity_views
from countries import views as country_views
from hierarchy import views as hierarchy_views
from search import views as search_views
from cookies import views as cookie_views
from feedback import views as feedback_views
from privacy_terms_and_conditions import views as privacy_terms_and_conditions_views
from admin.views import admin_login_view

urlpatterns = [
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('admin/login/', admin_login_view),
    path('admin/', admin.site.urls),
    path(
        'choose-country/', country_views.choose_country_view,
        name='choose-country'
    ),
    path('cookies/', cookie_views.CookiesView.as_view(), name="cookies"),
    re_path(
        r'commodity/(?P<commodity_code>\d{10})',
        commodity_views.commodity_detail, name='commodity-detail'
    ),
    path('search/', search_views.search_view, name='search-view'),
    path('feedback/', feedback_views.FeedbackView.as_view(), name='feedback-view'),
    path(
        'feedback/success/',
        feedback_views.FeedbackSuccessView.as_view(),
        name='feedback-success-view',
    ),

    re_path(r'hierarchy/(?P<node_id>.+)', hierarchy_views.hierarchy_view, name='hierarchy_node'),
    path('privacy-terms-and-conditions/', privacy_terms_and_conditions_views.PrivacyTermsAndConditionsView.as_view(), name="privacy_terms_and_conditions_views"),

]

"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('commodities/', views.commodity_list, name='commodity_list'),
    #re_path(r'^search/', include('haystack.urls')),
    re_path(r'^search*?', CommoditySearchView.as_view(), name='commodity-search-view'),

    re_path(r'section_data/(?P<section_id>\d+)', views.get_section_data),

    path(
        r'choose_country/', views.choose_country_view, name='choose-country'
    ),
    # path(
    #     r'search/', views.search_commodities_view, name='search-commodities'
    # ),

    re_path(
        r'headings/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_detail, name='heading-detail'
    ),
    re_path(
        r'heading_data/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_data, name='heading-data'
    ),

    #path('hierarchy/', hierarchy_views.hierarchy, name='hierarchy-view'),
    #path('hierarchy_data/', hierarchy_views.get_hierarchy_data),
    #path('hierarchy_data_cached/', hierarchy_views.get_hierarchy_data_cached),

    # re_path(
    #     r'headings/(?P<heading_code>(\d{10})|(\d{4}))', heading_views.heading_detail, name='heading-detail'
    # ),
    re_path(
        r'commodity_measures_table/(?P<commodity_code>\d{10})/(?P<origin_country>[a-zA-Z]{2})',
        commodity_views.get_measure_table_data, name='commodity-measures-table'
    ),
]
"""
