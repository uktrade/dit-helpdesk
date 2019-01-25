
from haystack import indexes

from requirements_documents.models import Commodity


# todo: this seems to supports elasticsearch 6: https://github.com/sabricot/django-elasticsearch-dsl


class CommodityIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/commodity_text.txt')

    #title = indexes.CharField(model_attr='tts_title', document=True)
    #heading_description = indexes.CharField(model_attr='tts_heading_description')

    def get_model(self):
        return Commodity

    def index_queryset(self, using=None):
        return self.get_model().objects.all()