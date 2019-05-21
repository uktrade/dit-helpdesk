from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from search.documents.commodity import CommodityDocument


class CommodityDocumentSerializer(DocumentSerializer):

    class Meta:
        document = CommodityDocument
        fields = (
            'id',
            'commodity_code',
            'description',
            'last_updated'
        )
