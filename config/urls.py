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

from flags.urls import flagged_re_path

from admin.views import admin_login_view
from commodities import views as commodity_views
from hierarchy import views as hierarchy_views
from cookies import views as cookie_views
from countries import views as country_views
from feedback import views as feedback_views
from contact import views as contact_views
from iee_contact import views as iee_contact_views
from healthcheck.views import HealthCheckView
from index import views as index
from privacy_terms_and_conditions import views as privacy_terms_and_conditions_views


handler404 = "core.views.error404handler"
handler500 = "core.views.error500handler"

urlpatterns = [
    # redirects to start page
    path("", index.IndexRedirect.as_view(), name="index"),
    path("auth/", include("authbroker_client.urls", namespace="authbroker")),
    path("choose-country/",
         country_views.ChooseCountryView.as_view(), name="choose-country"),
    re_path(
        r"^country/(?P<country_code>\w+)/information/$",
        country_views.CountryInformationView.as_view(),
        name="country-information",
    ),
    path(
        "country/location-autocomplete-graph.json",
        country_views.LocationAutocompleteView.as_view(),
        name="location-autocomplete",
    ),
    path("cookies/", cookie_views.CookiesView.as_view(), name="cookies"),
    path(
        "help/cookies/", cookie_views.CookieDetailsView.as_view(), name="cookie-details"
    ),
    re_path(
        r"^country/(?P<country_code>\w+)/section/(?P<section_id>\d{1,2})$",
        hierarchy_views.section_detail,
        name="section-detail",
    ),
    re_path(
        r"^country/(?P<country_code>\w+)/chapter/(?P<chapter_code>\d{10})/(?P<nomenclature_sid>\d+)$",
        hierarchy_views.ChapterDetailView.as_view(),
        name="chapter-detail",
    ),
    re_path(
        r"^country/(?P<country_code>\w+)/subheading/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)$",
        hierarchy_views.SubHeadingDetailView.as_view(),
        name="subheading-detail",
    ),
    flagged_re_path(
        "NI_JOURNEY",
        r"^country/(?P<country_code>\w+)/subheading/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)/northern-ireland/$",
        hierarchy_views.SubHeadingDetailNorthernIrelandView.as_view(),
        name="subheading-detail-northern-ireland",
    ),
    re_path(
        r"^country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})/(?P<nomenclature_sid>\d+)$",
        hierarchy_views.HeadingDetailView.as_view(),
        name="heading-detail",
    ),
    flagged_re_path(
        "NI_JOURNEY",
        r"^country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})/(?P<nomenclature_sid>\d+)/northern-ireland/$",
        hierarchy_views.HeadingDetailNorthernIrelandView.as_view(),
        name="heading-detail-northern-ireland",
    ),
    re_path(
        r"^country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)$",
        commodity_views.CommodityDetailView.as_view(),
        name="commodity-detail",
    ),
    flagged_re_path(
        "NI_JOURNEY",
        r"^country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)/northern-ireland/$",
        commodity_views.CommodityDetailNorthernIrelandView.as_view(),
        name="commodity-detail-northern-ireland",
    ),
    re_path(
        r"country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)"
        r"/import-measure/(?P<measure_id>\d{1,2})/conditions",
        commodity_views.MeasureConditionDetailView.as_view(),
        name="commodity-measure-conditions",
    ),
    re_path(
        r"country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})/(?P<nomenclature_sid>\d+)"
        r"/import-measure/(?P<measure_id>\d{1,2})/conditions",
        hierarchy_views.MeasureConditionDetailView.as_view(),
        name="heading-measure-conditions",
    ),
    re_path(
        r"country/(?P<country_code>\w+)/commodity/(?P<commodity_code>\d{10})/(?P<nomenclature_sid>\d+)"
        r"/import-measure/(?P<measure_id>\d{1,2})/quota/(?P<order_number>\d+)",
        commodity_views.MeasureQuotaDetailView.as_view(),
        name="commodity-measure-quota",
    ),
    re_path(
        r"country/(?P<country_code>\w+)/heading/(?P<heading_code>\d{10})/(?P<nomenclature_sid>\d+)"
        r"/import-measure/(?P<measure_id>\d{1,2})/quota/(?P<order_number>\d+)",
        hierarchy_views.MeasureQuotaDetailView.as_view(),
        name="heading-measure-quota",
    ),
    path(
        "feedback/", contact_views.ContactFormWizardView.as_view(), name="feedback-view"
    ),
    path(
        "contact/", contact_views.ContactFormWizardView.as_view(), name="contact-view"
    ),
    path(
        "iee_contact/",
        iee_contact_views.IEEContactFormWizardView.as_view(),
        name="iee-contact-view",
    ),
    path(
        "feedback/success/",
        feedback_views.FeedbackSuccessView.as_view(),
        name="feedback-success-view",
    ),
    path(
        "privacy-terms-and-conditions/",
        privacy_terms_and_conditions_views.PrivacyTermsAndConditionsView.as_view(),
        name="privacy_terms_and_conditions_views",
    ),
    path("check/", include("healthcheck.urls", namespace="healthcheck")),
    re_path("search/", include("search.urls", namespace="search")),
    path("accessibility/", include("accessibility.urls", namespace="accessibility")),
]


if settings.ADMIN_ENABLED:
    urlpatterns += [
        path("admin/login/", admin_login_view),
        path("admin/", admin.site.urls),
    ]


if settings.CMS_ENABLED:
    urlpatterns += [
        path("cms/", include("cms.urls")),
    ]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("", include(debug_toolbar.urls))] + urlpatterns
