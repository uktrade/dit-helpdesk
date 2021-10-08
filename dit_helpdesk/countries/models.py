from django.db import models


class Country(models.Model):
    # We have two country codes, one which represents the trading country code
    # and the other an optional alternative original country code.
    # e.g. https://www.gov.uk/guidance/change-to-the-eu-country-code-for-serbia-tariff-stop-press-notice-30
    country_code = models.CharField(max_length=2)  # ISO_3166-1_alpha-2 code
    alternative_non_trade_country_code = models.CharField(max_length=2, null=True)

    name = models.CharField(max_length=250)

    scenario = models.CharField(max_length=255, null=True)
    content_url = models.URLField(null=True, blank=True)

    has_eu_trade_agreement = models.BooleanField(default=False)
    trade_agreement_title = models.CharField(max_length=250, null=True)
    trade_agreement_type = models.CharField(max_length=250, null=True)

    is_eu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.country_code} - {self.name} - {self.scenario}"
