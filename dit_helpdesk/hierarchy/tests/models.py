from django.db import models

from ..models import Chapter, RulesOfOriginMixin


class RulesOfOriginMixinModel(models.Model, RulesOfOriginMixin):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

    def get_chapter(self):
        return self.chapter
