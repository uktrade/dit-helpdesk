from django.db import models


class Country(models.Model):

    country_code = models.CharField(max_length=2)  # ISO_3166-1_alpha-2 code
    name = models.CharField(max_length=250)

    def __str__(self):
        return '%s %s' % (self.country_code, self.name)