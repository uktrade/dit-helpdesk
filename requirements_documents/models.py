import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from psqlextra.manager import PostgresManager as _PostgresManager
from psqlextra.query import ConflictAction
from django.contrib.postgres.fields import ArrayField

from .tts_api import CommodityJson, SectionJson, HeadingJson, ChapterJson, CommodityHeadingJson

GROUP_NAME_CHOICES = [
    ('product_requirements', 'Product Requirements'),
    ('import_procedures', 'Import Procedures')
]


class PostgresManager(_PostgresManager):

    def bulk_upsert(self, conflict_target, rows, index_predicate=None):
        """
        For convenience (and consistency with django's bulk_create()) this
        is being overriden so it returns model objects instead of dictionaries.
        The only change is setting return_model=True.
        """

        if not rows or len(rows) <= 0:
            return

        self.on_conflict(conflict_target, ConflictAction.UPDATE, index_predicate)
        return self.bulk_insert(rows, return_model=True)


class Section(models.Model):

    section_id = models.CharField(max_length=30, unique=True)
    tts_json = JSONField(blank=True, null=True)

    @property
    def tts_obj(self):
        if self.tts_json is None:
            return None
        return SectionJson(self.tts_json)


class Chapter(models.Model):

    chapter_code = models.CharField(max_length=30)
    tts_json = JSONField(blank=True, null=True)

    section = models.ForeignKey(
        'Section', blank=True, null=True, on_delete=models.CASCADE
    )

    @property
    def tts_obj(self):
        if self.tts_json is None:
            return None
        return ChapterJson(self.tts_json)


class Heading(models.Model):

    heading_code = models.CharField(max_length=10, unique=True)
    heading_code_4 = models.CharField(max_length=4, unique=True, null=True, blank=True)

    tts_json = JSONField(blank=True, null=True)

    chapter = models.ForeignKey(
        'Chapter', blank=True, null=True, on_delete=models.CASCADE
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

'''

TODO:

class Commodity:
    - heading fk
    - abstract_commodity fk
    - tts_heading_json
    - tts_json
    
class AbstractCommodity:
    - heading fk
    - abstract_commodity fk
    - tts_heading_json

'''

# (Pdb) heading_leafs[0]['goods_nomenclature_sid']
# 93801
# (Pdb) heading_leafs[0]['goods_nomenclature_item_id']
# '0101300000'


class AbstractCommodity(models.Model):

    commodity_code = models.CharField(max_length=10)  # goods_nomenclature_item_id
    goods_nomenclature_sid = models.CharField(max_length=10)

    tts_heading_json = JSONField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'Heading', blank=True, null=True,
        related_name='children_abstract', on_delete=models.CASCADE
    )

    parent_abstract_commodity = models.ForeignKey(
        'AbstractCommodity', blank=True, null=True,
        related_name='children_abstract', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    @property
    def tts_heading_obj(self):
        if self.tts_heading_json is None:
            return None
        return CommodityHeadingJson(self.tts_heading_json)


class Commodity(models.Model):

    commodity_code = models.CharField(max_length=10, unique=True)
    goods_nomenclature_sid = models.CharField(max_length=10)

    requirement_documents = models.ManyToManyField(
        'RequirementDocument', through='HasRequirementDocument'
    )

    tts_json = JSONField(blank=True, null=True)
    tts_heading_json = JSONField(blank=True, null=True)

    tts_number_indents = models.IntegerField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    tts_section_position = models.IntegerField(blank=True, null=True)

    heading = models.ForeignKey(
        'Heading', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )
    parent_abstract_commodity = models.ForeignKey(
        'AbstractCommodity', blank=True, null=True,
        related_name='children_concrete', on_delete=models.CASCADE
    )

    document_titles = models.ManyToManyField(
        'EuTradeHelpdeskDocumentTitle', through='CommodityHasDocTitle'
    )

    objects = models.Manager()
    pg_objects = PostgresManager()

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
        return CommodityJson(self.tts_json)  #, commodity_code=self.commodity_code)

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


class EuTradeHelpdeskDocumentTitle(models.Model):
    title = models.CharField(max_length=999, unique=True)
    #group_name = models.CharField(max_length=120, choices=GROUP_NAME_CHOICES)
    #origin_country = models.CharField(max_length=10)
    #commodity = models.ForeignKey('Commodity', on_delete=models.CASCADE)


class CommodityHasDocTitle(models.Model):
    commodity = models.ForeignKey('Commodity', on_delete=models.CASCADE)
    document_title = models.ForeignKey('EuTradeHelpdeskDocumentTitle', on_delete=models.CASCADE)
    origin_country = models.CharField(max_length=120)

    class Meta:
        unique_together = ('commodity', 'document_title', 'origin_country')


class EuTradeHelpdeskDocument(models.Model):

    title = models.CharField(max_length=200)
    group_name = models.CharField(max_length=120, choices=GROUP_NAME_CHOICES)

    query_urls = ArrayField(models.CharField(max_length=900), default=list)

    fragment1 = models.ForeignKey(
        'RequirementDocument', blank=True, null=True,
        on_delete=models.CASCADE, related_name='eu_trade_helpdesk_documents1'
    )
    fragment2 = models.ForeignKey(
        'RequirementDocument', blank=True, null=True,
        on_delete=models.CASCADE, related_name='eu_trade_helpdesk_documents2'
    )
    selenium_elem_html = models.CharField(max_length=6000, blank=True, null=True)
    origin_country = models.CharField(max_length=10)
    commodity = models.ForeignKey('Commodity', on_delete=models.CASCADE)

    def __str__(self):
        return 'EuTradeHelpdeskDocument "%s" - %s' % (
            self.title, self.commodity.commodity_code
        )

    def get_absolute_url(self):
        return reverse('eu-document', kwargs={'pk': self.pk})


class HasRequirementDocument(models.Model):

    commodity = models.ForeignKey('Commodity', on_delete=models.CASCADE)
    document = models.ForeignKey('RequirementDocument', on_delete=models.CASCADE)
    eu_trade_helpdesk_website_destination_country = models.CharField(max_length=120)
    eu_trade_helpdesk_website_origin_country = models.CharField(max_length=120)
    eu_trade_helpdesk_website_label = models.CharField(max_length=120)

    objects = models.Manager()
    pg_objects = PostgresManager()

    UNIQUENESS_FIELDS = [
        'commodity', 'document',
        'eu_trade_helpdesk_website_destination_country',
        'eu_trade_helpdesk_website_origin_country',
    ]
    ALL_FIELDS = UNIQUENESS_FIELDS + ['eu_trade_helpdesk_website_label']

    class Meta:
        unique_together = (
            'commodity', 'document',
            'eu_trade_helpdesk_website_destination_country',
            'eu_trade_helpdesk_website_origin_country',
        )

    def __str__(self):
        return '%s %s' % (self.commodity.pk, self.document.pk)


class RequirementDocument(models.Model):
    # https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=GB&lang=en&code=heafocon&reqType=s
    # https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=heafocon&reqType=s
    code = models.CharField(max_length=80)
    requirement_type = models.CharField(max_length=80)
    destination_country = models.CharField(max_length=80)
    language = models.CharField(max_length=80)

    html = models.TextField(null=True, blank=True)
    html_normalised = models.TextField(null=True, blank=True)
    query_url = models.CharField(max_length=250)

    objects = models.Manager()
    pg_objects = PostgresManager()

    UNIQUENESS_FIELDS = [
        'code', 'requirement_type', 'destination_country',
        'language'
    ]
    ALL_FIELDS = UNIQUENESS_FIELDS + [
        'html', 'html_normalised', 'query_url'
    ]

    class Meta:
        unique_together = ('code', 'requirement_type', 'destination_country', 'language')

    @property
    def document_title(self):
        return '%s %s %s' % (
            self.code, self.requirement_type, self.destination_country
        )

    def get_absolute_url(self):
        kwargs = {'document_pk': self.pk}
        return reverse('document-detail', kwargs=kwargs)

    def get_id_key(self):
        """
        Used by get_eu_requirements_documents for checking for duplicates
        """
        li = [getattr(self, k) for k in RequirementDocument.UNIQUENESS_FIELDS]
        return tuple(li)

'''
    url2 = "https://trade.ec.europa.eu/services/reqs/public/v1//requirement?destinationCountry=eu&lang=en&code=" + code + "&reqType=" + requirement_type
    response = requests.get(url2)
    key = commodity + '__' + code
    if key in requirements_texts:
        import pdb; pdb.set_trace()
    requirements_texts[key] = fhtml(response.text)
'''

# estinationCountry=eu&lang=en&code=