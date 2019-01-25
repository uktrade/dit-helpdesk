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

from requirements_documents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('commodities/', views.commodity_list, name='commodity_list'),
    re_path(
        r'commodity/(?P<commodity_code>\d{10})',
        views.commodity_detail, name='commodity-detail'
    ),
    re_path(r'^search/', include('haystack.urls')),

    re_path(
        r'eu_document/(?P<pk>\d+)',
        views.eu_document_detail, name='eu-document'
    ),

    re_path(
        r'document/(?P<document_pk>\d+)',
        views.document_detail, name='document-detail'
    ),
    path('hierarchy/', views.hierarchy, name='hierarchy'),
    path('hierarchy_data/', views.get_hierarchy_data),

    re_path(
        r'commodity_measures_table/(?P<commodity_code>\d{10})',
        views.get_measure_table_data, name='commodity-measures-table'
    ),

    re_path(
        r'headings/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_detail, name='heading-detail'
    ),
    re_path(
        r'heading_data/(?P<heading_code>(\d{10})|(\d{4}))', views.heading_data, name='heading-data'
    ),

]
