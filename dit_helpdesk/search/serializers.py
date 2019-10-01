from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from search.documents.commodity import CommodityDocument
from search.documents.chapter import ChapterDocument
from search.documents.heading import HeadingDocument
from search.documents.section import SectionDocument
from search.documents.subheading import SubHeadingDocument
from search.forms import CommoditySearchForm


class CommodityDocumentSerializer(DocumentSerializer):

    class Meta:
        document = CommodityDocument
        fields = (
            'id',
            'commodity_code',
            'description',
            'keywords',
            'ranking',
            'last_updated',
            '_score'
        )


class ChapterDocumentSerializer(DocumentSerializer):

    class Meta:
        document = ChapterDocument
        fields = (
            'id',
            'commodity_code',
            'description',
            'keywords',
            'ranking',
        )


class HeadingDocumentSerializer(DocumentSerializer):

    class Meta:
        document = HeadingDocument
        fields = (
            'id',
            'commodity_code',
            'description',
            'keywords',
            'ranking',
        )


class SubHeadingDocumentSerializer(DocumentSerializer):

    class Meta:
        document = SubHeadingDocument
        fields = (
            'id',
            'commodity_code',
            'description',
            'keywords',
            'ranking',
        )


class SectionDocumentSerializer(DocumentSerializer):

    class Meta:
        document = SectionDocument
        fields = (
            'id',
            'section_id',
            'title',
            'keywords',
            'ranking',
        )

class CommoditySearchSerializer(serializers.Serializer):
    q = serializers.CharField()
    page = serializers.IntegerField(default=1)


class HierarchySearchSerializer(serializers.Serializer):
    country_code = serializers.CharField()
    node_id = serializers.CharField(default='root')
