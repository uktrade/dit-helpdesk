from django.db import models


class Country(models.Model):

    country_code = models.CharField(max_length=2)  # ISO_3166-1_alpha-2 code
    name = models.CharField(max_length=250)

    scenario = models.CharField(max_length=255)
    content_url = models.URLField(null=True, blank=True)

    has_uk_trade_agreement = models.BooleanField(default=False)
    has_eu_trade_agreement = models.BooleanField(default=False)

    is_eu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.country_code} - {self.name} - {self.scenario}"
