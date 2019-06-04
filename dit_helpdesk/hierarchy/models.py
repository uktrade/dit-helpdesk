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
    """
    Model representing the top level section of the hierarchy
    """

    section_id = models.IntegerField(unique=True)
    tts_json = models.TextField(blank=True, null=True)
    roman_numeral = models.CharField(max_length=5, null=True)
    title = models.TextField(blank=True, null=True)
    position = models.IntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    def __str__(self):
        return "Section {0}".format(self.roman_numeral)

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'section-%s' % self.pk

    @property
    def chapter_range_str(self):
        """
        Property method returning a string representing the range of chapters in this section
        :return:  string
        """
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
    def tts_obj(self):
        """
        Property method returning the SectionJson object representing the data stored in the tts_json field
        :return: SectionJson object
        """
        return SectionJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        """
        Property method returning the Section title from the SectionJson object
        :return: string
        """
        return self.tts_obj.title

    def get_hierarchy_children(self):
        """
        Query returning a list of child chapters ordered by code
        :return:
        """
        return self.chapter_set.all().order_by('chapter_code')

    def get_chapters_url(self):
        """
        Returns a section url to a view listing the child chapters
        :return:
        """
        return reverse(
            'hierarchy-section-chapters',
            kwargs={'section_id': str(self.section_id)}
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'section-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)


class Chapter(models.Model):
    """
    Model representing the second level chapters of the hierarchy
    """

    # goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    productline_suffix = models.CharField(max_length=2, null=True)
    leaf = models.BooleanField(blank=True, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    chapter_code = models.CharField(max_length=30)
    tts_json = models.TextField(blank=True, null=True)

    section = models.ForeignKey(
        'Section', blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return "Chapter {0}".format(self.chapter_code)

    @property
    def commodity_code(self):
        return self.chapter_code

    @property
    def title(self):
        """
        Property method returning the Chapter title from the object field
        :return: string
        """
        return self.description

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'chapter-%s' % self.pk

    @property
    def tts_obj(self):
        """
        Property method returning the ChapterJson object representing the data stored in the tts_json field
        :return: ChapterJson object
        """
        return ChapterJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        """
        Property method returning the Chapter title from the ChapterJson object
        :return: string
        """
        return self.tts_obj.title

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.chapter_code

    def get_hierarchy_children(self):
        """
        Query returning a list of child Headings ordered by code
        :return:
        """
        children = []
        for heading in self.headings.all().order_by('heading_code'):
            for child in heading.get_hierarchy_children():
                if heading.heading_code != child.commodity_code:
                    children.append(heading)
                else:
                    children.append(child)
        return children

    def get_headings_url(self):
        """
        Returns a chapter url to a view listing the child headings
        :return:
        """
        return reverse(
            'hierarchy-section-chapter-headings',
            kwargs={'chapter_code_2': self.chapter_code[:2]}
        )

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'chapter-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)


class Heading(models.Model):
    goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    productline_suffix = models.CharField(max_length=2, null=True)
    leaf = models.BooleanField(blank=True, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

    heading_code = models.CharField(max_length=10)
    heading_code_4 = models.CharField(
        max_length=4, null=True, blank=True
    )

    tts_json = models.TextField(blank=True, null=True)

    chapter = models.ForeignKey(
        'hierarchy.Chapter', blank=True, null=True, on_delete=models.CASCADE,
        related_name='headings'
    )

    @property
    def commodity_code(self):
        return self.heading_code

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'heading-%s' % self.pk

    @property
    def tts_obj(self):
        """
        Property method returning the HeadingJson object representing the data stored in the tts_json field
        :return: HeadingJson object
        """
        return HeadingJson(json.loads(self.tts_json))

    @property
    def tts_title(self):
        """
        Property method returning the Heading title from the object field
        :return: string
        """
        return self.description

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.heading_code

    def __str__(self):
        return "Heading {0}".format(self.heading_code)

    def get_absolute_url(self):
        """
        Method returning the rul of the current instance
        :return:
        """
        kwargs = {'heading_code': self.heading_code_4 or self.heading_code}
        return reverse('heading-detail', kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [obj for obj in self.child_subheadings.all().order_by('commodity_code')]
        commodities = [obj for obj in self.children_concrete.all().order_by('commodity_code')]
        return commodities + sub_headings

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'heading-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)


class SubHeading(models.Model):
    productline_suffix = models.CharField(max_length=2, null=True)
    parent_goods_nomenclature_item_id = models.CharField(max_length=10, null=True)
    parent_goods_nomenclature_sid = models.CharField(max_length=10, null=True)
    parent_productline_suffix = models.CharField(max_length=2, null=True)
    description = models.TextField(null=True)
    number_indents = models.SmallIntegerField(null=True)
    keywords = models.TextField()
    ranking = models.SmallIntegerField(null=True)

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
        unique_together = ('commodity_code', 'description')

    def __str__(self):
        return "Sub Heading {0}".format(self.commodity_code)

    @property
    def hierarchy_key(self):
        """
        Property method returning the key used to identify the node in the hierarchy html of the search view template
        :return: string
        """
        return 'sub_heading-%s' % self.pk

    @property
    def tts_heading_obj(self):
        """
        Property method returning the CommodityHeadingJson object representing the data stored in the tts_json field
        :return: CommodityHeadingJson object
        """
        return CommodityHeadingJson(json.loads(self.tts_heading_json))

    @property
    def tts_title(self):
        """
        Property method returning the SubHeading title from the object field
        :return: string
        """
        return self.description

    @property
    def tts_heading_description(self):
        """
        Property method returning the SubHeading title from the object field
        :return: string
        """
        return self.description

    @property
    def harmonized_code(self):
        """
        property method used across all hierarchy model instances, apart from Section, to normalise the code
        name field for the sake of consistency
        :return: string representing ten digit code
        """
        return self.commodity_code

    def get_parent(self):
        """
        Method to return the parent Heading or Subheading of the current instance
        :return: Model instance
        """
        return self.heading or self.parent_subheading

    def get_hierarchy_url(self, country_code=None):
        """
        Return the url of the model instance as used in the hierarchy html
        :param country_code: string representing the country code
        :return: url
        """
        kwargs = {
            'node_id': 'sub_heading-%s' % self.pk
        }

        if country_code is not None:
            kwargs['country_code'] = country_code.lower()

        return reverse('search:search-hierarchy', kwargs=kwargs)

    def get_hierarchy_children(self):
        """
        Query returning a list of child SubHeadings and/or Commodities ordered by code
        :return:
        """
        sub_headings = [obj for obj in self.child_subheadings.all().order_by('commodity_code')]
        commodities = [obj for obj in self.children_concrete.all().order_by('commodity_code')]
        return commodities + sub_headings
