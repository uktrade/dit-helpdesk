from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields

from hierarchy.models import Chapter, Section, Heading
from search.documents.util import html_strip

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@INDEX.doc_type
class ChapterDocument(DocType):
    """
    Chapter elasticsearch document
    """
    #
    # section = fields.ObjectField(properties={
    #     'section_id': fields.TextField(),
    #     'title': fields.TextField(),
    # })
    #
    # headings = fields.NestedField(properties={
    #     'description': fields.TextField(),
    #     'heading_code': fields.TextField()
    # })

    id = fields.IntegerField(attr='id')

    commodity_code = fields.KeywordField(
        attr="chapter_code",
        # analyzer=html_strip,
        # fields={
        #     'commodity_code.raw': fields.StringField(analyzer="Keyword")
        # }
    )

    description = fields.TextField(
        analyzer=html_strip,
        # fields={
        #     'description.raw': fields.StringField(analyzer="Keyword")
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
        model = Chapter

    #     related_models = [Heading, Section]
    #
    # def get_queryset(self):
    #     """Not mandatory but to improve performance we can select related in one sql request"""
    #     return super(ChapterDocument, self).get_queryset().select_related(
    #         'section'
    #     )
    #
    # def get_instances_from_related(self, related_instance):
    #     """If related_models is set, define how to retrieve the Car instance(s) from the related model.
    #     The related_models option should be used with caution because it can lead in the index
    #     to the updating of a lot of items.
    #     """
    #     if isinstance(related_instance, Section):
    #         return related_instance.chapter_set.all()
    #     elif isinstance(related_instance, Heading):
    #         return related_instance.chapter
