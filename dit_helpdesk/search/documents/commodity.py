from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields

from commodities.models import Commodity
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(number_of_shards=1, number_of_replicas=0)


@INDEX.doc_type
class CommodityDocument(DocType):
    """
    Commodity elasticsearch document
    """

    id = fields.IntegerField(attr="goods_nomenclature_sid")

    commodity_code = fields.KeywordField()

    description = fields.TextField(analyzer=html_strip, fielddata=True)

    keywords = fields.TextField(analyzer=html_strip)

    hierarchy_context = fields.TextField(attr="ancestor_data")

    node_id = fields.TextField(attr="hierarchy_key")

    ranking = fields.IntegerField()

    class Meta:
        model = Commodity
