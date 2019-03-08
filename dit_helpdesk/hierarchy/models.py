import json

from django.db import models
from django.urls import reverse

from trade_tariff_service.tts_api import ChapterJson, CommodityHeadingJson, HeadingJson, SectionJson


ROMAN_NUMERALS = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
    7: 'VII',
    8: 'VIII',
    9: 'IX',
    10: 'X',
    11: 'XI',
    12: 'XII',
    13: 'XIII',
    14: 'XIV',
    15: 'XV',
    16: 'XVI',
    17: 'XVII',
    18: 'XVIII',
    19: 'XIX',
    20: 'XX',
    21: 'XXI'
}


class Section(models.Model):

    section_id = models.IntegerField(unique=True)
    tts_json = models.TextField(blank=True, null=True)

    @property
    def hierarchy_key(self):
        return 'section-%s' % self.pk

    @property
    def chapter_range_str(self):
        chapter_codes = [
            int(chapter.chapter_code[:2]) for chapter in self.chapter_set.all()
        ]
        if len(chapter_codes) == 0:
            return 'None'
        if len(chapter_codes) == 1:
            return str(chapter_codes[0])
        min_code, max_code = min(chapter_codes), max(chapter_codes)
        return '%s to %s' % (min_code, max_code)

    @property
    def roman_numeral(self):
        # or: return ROMAN_NUMERALS[int(self.section_id)]
        return self.tts_obj.numeral

    @property
    def tts_obj(self):
        return SectionJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        return self.tts_obj.title

    def get_hierarchy_children(self):
        return self.chapter_set.all()

    def get_chapters_url(self):
        return reverse(
            'hierarchy-section-chapters',
            kwargs={'section_id': str(self.section_id)}
        )

    def get_hierarchy_url(self, country_code=None):
        kwargs = {'node_id': 'section-%s' % self.pk}
        if country_code is not None:
           kwargs['country_code'] = country_code.lower()
        return reverse('hierarchy_node', kwargs=kwargs)


class Chapter(models.Model):

    chapter_code = models.CharField(max_length=30)
    tts_json = models.TextField(blank=True, null=True)

    section = models.ForeignKey(
        'Section', blank=True, null=True, on_delete=models.CASCADE
    )

    @property
    def hierarchy_key(self):
        return 'chapter-%s' % self.pk

    @property
    def tts_obj(self):
        return ChapterJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        return self.tts_obj.title

    @property
    def harmonized_code(self):
        return self.chapter_code

    def get_hierarchy_children(self):
        return self.headings.all()

    def get_headings_url(self):
        return reverse(
            'hierarchy-section-chapter-headings',
            kwargs={'chapter_code_2': self.chapter_code[:2]}
        )

    def get_hierarchy_url(self, country_code=None):
        kwargs = {'node_id': 'chapter-%s' % self.pk}
        if country_code is not None:
           kwargs['country_code'] = country_code.lower()
        return reverse('hierarchy_node', kwargs=kwargs)


class Heading(models.Model):

    heading_code = models.CharField(max_length=10, unique=True)
    heading_code_4 = models.CharField(
        max_length=4, unique=True, null=True, blank=True
    )

    tts_json = models.TextField(blank=True, null=True)

    chapter = models.ForeignKey(
        'hierarchy.Chapter', blank=True, null=True, on_delete=models.CASCADE,
        related_name='headings'
    )

    @property
    def hierarchy_key(self):
        return 'heading-%s' % self.pk

    @property
    def tts_obj(self):
        return HeadingJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        return self.tts_obj.title

    @property
    def harmonized_code(self):
        return self.heading_code

    def __str__(self):
        return 'Heading ' + self.heading_code[:4]

    def get_absolute_url(self):
        kwargs = {'heading_code': self.heading_code_4 or self.heading_code}
        return reverse('heading-detail', kwargs=kwargs)

    '''
    # this was used for indexing Headings for search
    def get_search_index_words(self):
        words = self.tts_title
        for commodity in self.get_commodities_flattened():
            words = words + ' ' + commodity.tts_title

        words = words.replace('Other', ' ').replace('other', ' ').replace('  ', ' ')
        return words
    '''

    def get_hierarchy_children(self):
        sub_headings = [obj for obj in self.child_subheadings.all()]
        commodities = [obj for obj in self.children_concrete.all()]
        return commodities + sub_headings

    def get_hierarchy_url(self, country_code=None):
        kwargs = {'node_id': 'heading-%s' % self.pk}
        if country_code is not None:
           kwargs['country_code'] = country_code.lower()
        return reverse('hierarchy_node', kwargs=kwargs)


class SubHeading(models.Model):

    commodity_code = models.CharField(max_length=10)  # goods_nomenclature_item_id
    goods_nomenclature_sid = models.CharField(max_length=10)

    tts_heading_json = models.TextField(blank=True, null=True)
    tts_is_leaf = models.BooleanField(blank=True, null=True)

    heading = models.ForeignKey(
        'hierarchy.Heading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    parent_subheading = models.ForeignKey(
        'hierarchy.Subheading', blank=True, null=True,
        related_name='child_subheadings', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('commodity_code', 'goods_nomenclature_sid')

    @property
    def hierarchy_key(self):
        return 'sub_heading-%s' % self.pk

    @property
    def tts_heading_obj(self):
        return CommodityHeadingJson(json.loads(self.tts_heading_json))

    @property
    def tts_title(self):
        return self.tts_heading_obj.title

    @property
    def tts_heading_description(self):
        return self.tts_heading_obj.title

    @property
    def harmonized_code(self):
        return self.commodity_code

    def get_parent(self):
        return self.heading or self.parent_subheading

    def get_hierarchy_url(self, country_code=None):
        kwargs = {'node_id': 'sub_heading-%s' % self.pk}
        if country_code is not None:
           kwargs['country_code'] = country_code.lower()
        return reverse('hierarchy_node', kwargs=kwargs)

    def get_hierarchy_children(self):
        sub_headings = [obj for obj in self.child_subheadings.all()]
        commodities = [obj for obj in self.children_concrete.all()]
        return commodities + sub_headings
