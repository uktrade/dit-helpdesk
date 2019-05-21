from django.conf import settings
from elasticsearch_dsl import analyzer

from django_elasticsearch_dsl import DocType, Index, fields

from commodities.models import Commodity


# Name of the Elasticsearch index

commodity = Index('commodities')

# See Elasticsearch Indices API reference for available settings
commodity.settings(
    number_of_shards=1,
    number_of_replicas=0
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

@commodity.doc_type
class CommodityDocument(DocType):
    """
    Commodity elasticsearch document
    """

    # id = fields.IntegerField(attr="id")
    #
    commodity_code = fields.StringField(
        analyzer=html_strip,
        fields={
            'raw': fields.StringField(analyzer='keyword'),
        }
    )
    #
    # description = fields.TextField(
    #     analyzer=html_strip,
    #     fields={
    #         'raw': fields.TextField(analyzer='keyword'),
    #     }
    # )
    # last_updated = fields.DateField()

    class Meta:
        model = Commodity
        # fields = [
        #     'commodity_code',
        # ]
