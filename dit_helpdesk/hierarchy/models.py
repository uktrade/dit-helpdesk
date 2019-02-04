from django.contrib.postgres.fields import JSONField
from django.db import models

from trade_tariff_service.tts_api import SectionJson, ChapterJson


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