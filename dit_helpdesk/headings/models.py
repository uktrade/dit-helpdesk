from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

from trade_tariff_service.tts_api import CommodityHeadingJson, HeadingJson


class Heading(models.Model):

    heading_code = models.CharField(max_length=10, unique=True)
    heading_code_4 = models.CharField(
        max_length=4, unique=True, null=True, blank=True
    )

    tts_json = JSONField(blank=True, null=True)

    chapter = models.ForeignKey(
        'hierarchy.Chapter', blank=True, null=True, on_delete=models.CASCADE
    )

    @property
    def tts_obj(self):
        if self.tts_json is None:
            return None
        return HeadingJson(self.tts_json)

    @property
    def tts_title(self):
        if self.tts_json is None:
            return 'NO TITLE'
        return self.tts_obj.title

    def __str__(self):
        return 'Heading '+self.heading_code[:4]

    def get_absolute_url(self):
        kwargs = {'heading_code': self.heading_code_4 or self.heading_code}
        return reverse('heading-detail', kwargs=kwargs)

    def get_commodities_flattened(self):
        from headings.views import get_heading_data
        return get_heading_data(self, '')[2]

    def get_commodity_keys_flattened(self):
        commodities = self.get_commodities_flattened()
        return [
            (o.__class__.__name__, o.pk) for o in commodities
        ]

    def get_search_index_words(self):

        words = self.tts_title
        for commodity in self.get_commodities_flattened():
            words = words + ' ' + commodity.tts_title

        words = words.replace('NO_TITLE', ' ')  # just in case
        words = words.replace('Other', ' ').replace('other', ' ').replace('  ', ' ')
        return words


class SubHeading(models.Model):

    commodity_code = models.CharField(max_length=10)  # goods_nomenclature_item_id
    goods_nomenclature_sid = models.CharField(max_length=10)

    tts_heading_json = JSONField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'headings.Heading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    parent_subheading = models.ForeignKey(
        'headings.Subheading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    @property
    def tts_heading_obj(self):
        if self.tts_heading_json is None:
            return None
        return CommodityHeadingJson(self.tts_heading_json)

    @property
    def tts_title(self):
        if self.tts_heading_json is None:
            return 'NO_TITLE'
        return self.tts_heading_obj.title

    @property
    def tts_heading_description(self):
        if self.tts_heading_json is None:
            return 'NO_TITLE'
        return self.tts_heading_obj.title

    def get_parent(self):
        return self.heading or self.parent_subheading

