import json
import re

from django.db import models
from django.urls import reverse

from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson

COMMODITY_CODE_REGEX = '([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})'


class Commodity(models.Model):

    commodity_code = models.CharField(max_length=10, unique=True)
    goods_nomenclature_sid = models.CharField(max_length=10)

    tts_json = models.TextField(blank=True, null=True)
    tts_heading_json = models.TextField(blank=True, null=True)

    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'hierarchy.Heading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )
    parent_subheading = models.ForeignKey(
        'hierarchy.SubHeading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )

    objects = models.Manager()

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    @property
    def hierarchy_key(self):
        return 'commodity-%s' % self.pk

    def __str__(self):
        return 'Commodity %s' % self.commodity_code

    def get_absolute_url(self):
        kwargs = {'commodity_code': self.commodity_code}
        return reverse('commodity-detail', kwargs=kwargs)

    @property
    def commodity_code_split(self):
        code_match_obj = re.search(COMMODITY_CODE_REGEX, self.commodity_code)
        return [code_match_obj.group(i) for i in range(1, 5)]

    @property
    def tts_obj(self):
        return CommodityJson(json.loads(self.tts_json))

    @property
    def tts_heading_obj(self):
        return CommodityHeadingJson(json.loads(self.tts_heading_json))

    @property
    def tts_title(self):
        return self.tts_obj.title

    @property
    def tts_heading_description(self):
        return self.tts_obj.heading_description

    def get_heading(self):
        """Got up the hierarchy of sub-headings and return the Heading"""
        from hierarchy.models import Heading
        obj = self.heading or self.parent_subheading
        while type(obj) is not Heading:
            obj = obj.get_parent()
        return obj
