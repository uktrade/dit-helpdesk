from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from search.documents.commodity import CommodityDocument
    # , ChapterDocument, HeadingDocument, SubHeadingDocument, \
    # SectionDocument


from search.documents.chapter import ChapterDocument
from search.documents.heading import HeadingDocument
from search.documents.section import SectionDocument
from search.documents.subheading import SubHeadingDocument


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