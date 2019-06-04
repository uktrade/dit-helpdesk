from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields

from hierarchy.models import Section, Chapter
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@INDEX.doc_type
class SectionDocument(DocType):
    """
    Chapter elasticsearch document
    """

    # chapter_set = fields.NestedField(properties={
    #     'description': fields.TextField(),
    #     'chapter_code': fields.TextField()
    # })

    id = fields.IntegerField(attr='id')

    commodity_code = fields.KeywordField(
        attr="section_id",
        # analyzer=html_strip,
        # fields={
        #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    description = fields.TextField(
        attr="title",
        analyzer=html_strip,
        # fields={
        #     'title.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    keywords = fields.TextField(
        analyzer=html_strip,
        # fields={
        #     'keywords.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    ranking = fields.IntegerField()

    class Meta:
        model = Section

        # related_models = [Chapter]

    # def get_instances_from_related(self, related_instance):
    #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
    #     The related_models option should be used with caution because it can lead in the index
    #     to the updating of a lot of items.
    #     """
    #     if isinstance(related_instance, Chapter):
    #         return related_instance.chapter_set.all()