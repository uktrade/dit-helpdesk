from django.db import models


class Country(models.Model):
    # We have two country codes, one which represents the trading country code
    # and the other an optional alternative original country code.
    # e.g. https://www.gov.uk/guidance/change-to-the-eu-country-code-for-serbia-tariff-stop-press-notice-30
    country_code = models.CharField(max_length=2)  # ISO_3166-1_alpha-2 code
    alternative_non_trade_country_code = models.CharField(max_length=2, null=True)

    name = models.CharField(max_length=250)

    scenario = models.CharField(max_length=255)
    content_url = models.URLField(null=True, blank=True)

    has_uk_trade_agreement = models.BooleanField(default=False)
    has_eu_trade_agreement = models.BooleanField(default=False)
    trade_agreement_title = models.CharField(max_length=250, null=True)
    trade_agreement_type = models.CharField(max_length=250, null=True)

    is_eu = models.BooleanField(default=False)

    # These 2 fields are temporary and will replace scenario and content_url fields above
    # scenario needs to be null for now or existing entries will break
    new_scenario = models.CharField(max_length=255, null=True)
    new_trade_agreement_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.country_code} - {self.name} - {self.scenario}"
