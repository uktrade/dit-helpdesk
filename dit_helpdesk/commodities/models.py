from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
#from django.contrib.postgres.fields import ArrayField


from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson


class Commodity(models.Model):

    commodity_code = models.CharField(max_length=10, unique=True)
    goods_nomenclature_sid = models.CharField(max_length=10)

    # requirement_documents = models.ManyToManyField(
    #     'RequirementDocument', through='HasRequirementDocument'
    # )

    tts_json = JSONField(blank=True, null=True)
    tts_heading_json = JSONField(blank=True, null=True)

    tts_number_indents = models.IntegerField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    tts_section_position = models.IntegerField(blank=True, null=True)

    heading = models.ForeignKey(
        'headings.Heading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )
    parent_subheading = models.ForeignKey(
        'headings.SubHeading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )

    # document_titles = models.ManyToManyField(
    #     'EuTradeHelpdeskDocumentTitle', through='CommodityHasDocTitle'
    # )

    objects = models.Manager()
    #pg_objects = PostgresManager()

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    def __str__(self):
        return 'Commodity %s' % self.commodity_code

    def get_absolute_url(self):
        kwargs ={'commodity_code': self.commodity_code}
        return reverse('commodity-detail', kwargs=kwargs)

    def refresh_fields(self):
        if self.tts_json is None:
            return
        self.tts_section_position = self.tts_obj.section_position
        self.tts_number_indents = self.tts_obj.di['number_indents']
        self.save()

    @property
    def tts_obj(self):
        if self.tts_json is None:
            return None
        return CommodityJson(self.tts_json)

    @property
    def tts_heading_obj(self):
        if self.tts_heading_json is None:
            return None
        return CommodityHeadingJson(self.tts_heading_json)

    @property
    def tts_title(self):
        if self.tts_json is None:
            return 'WARNING: .tts_title requested when tts_json is None'
        return self.tts_obj.title

    @property
    def tts_heading_description(self):
        if self.tts_json is None:
            return 'WARNING: .tts_title requested when tts_json is None'
        return self.tts_obj.heading_description

    @property
    def tts_summary(self):
        if self.tts_json is None:
            return 'WARNING: .tts_summary requested when tts_json is None'
        tts_obj = self.tts_obj
        summary = '  %s %s %s' % (self.tts_title, tts_obj.section_position, tts_obj.chapter_title)
        indent = '--- ' * tts_obj.di['number_indents']
        return indent + summary

    def get_heading(self):
        from headings.models import Heading
        obj = self.heading or self.parent_subheading
        while type(obj) is not Heading:
            obj = obj.get_parent()
        return obj