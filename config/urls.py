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
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include

from admin.views import admin_login_view
from commodities import views as commodity_views
from hierarchy import views as hierarchy_views
from cookies import views as cookie_views
from countries import views as country_views
from feedback import views as feedback_views
from healthcheck.views import HealthCheckView
from index import views as index
from privacy_terms_and_conditions import views as privacy_terms_and_conditions_views


handler404 = 'core.views.error404handler'
handler500 = 'core.views.error500handler'

urlpatterns = [

    path(
        '',
        index.IndexRedirect.as_view(),
        name="index"
    ),

    path(
        'auth/',
        include('authbroker_client.urls',
                namespace='authbroker')
    ),

    path(
        'choose-country/',
        country_views.choose_country_view,
        name='choose-country'
    ),

    path(
        'cookies/',
        cookie_views.CookiesView.as_view(),
        name="cookies"
    ),

    re_path(
        r'^country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})$',
        commodity_views.commodity_detail,
        name='commodity-detail'
    ),

    re_path(
        r'^country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})$',
        hierarchy_views.heading_detail,
        name='heading-detail'
    ),

    re_path(
        r'country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})'
        r'/import-measure/(?P<measure_id>\d{1,2})/conditions',
        commodity_views.measure_condition_detail,
        name='commodity-measure-conditions'
    ),

    re_path(
        r'country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})'
        r'/import-measure/(?P<measure_id>\d{1,2})/conditions',
        hierarchy_views.measure_condition_detail,
        name='heading-measure-conditions'
    ),

    # path(
    #     'feedback/',
    #     feedback_views.FeedbackView.as_view(),
    #     name='feedback-view'
    # ),

    path(
        'feedback/',
        feedback_views.FeedbackFormWizardView.as_view(),
        name='feedback-view'
    ),

    path(
        'feedback/success/',
        feedback_views.FeedbackSuccessView.as_view(),
        name='feedback-success-view',
    ),

    # re_path('feedback/', include('feedback.urls', namespace="feedback")),

    path(
        'privacy-terms-and-conditions/',
        privacy_terms_and_conditions_views.PrivacyTermsAndConditionsView.as_view(),
         name="privacy_terms_and_conditions_views"
    ),

    re_path(
        r'^check/$',
        HealthCheckView.as_view(),
        name='healthcheck'
    ),

    re_path('search/', include('search.urls', namespace="search")),
]


if settings.ADMIN_ENABLED:
    urlpatterns += [
        path('admin/login/', admin_login_view),
        path('admin/', admin.site.urls)
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('', include(debug_toolbar.urls)),
    ] + urlpatterns

