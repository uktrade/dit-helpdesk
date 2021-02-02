import datetime as dt

from django.db import models

from countries.models import Country


class RulesDocument(models.Model):
    """
    Rules Of Origin Document optionally related to a Country Group
    """
    nomenclature_tree = models.ForeignKey(
        "hierarchy.NomenclatureTree", on_delete=models.CASCADE, null=True)

    description = models.TextField()
    countries = models.ManyToManyField(Country, related_name='rules_documents')
    source_url = models.URLField(null=True, blank=True)
    start_date = models.DateField(default=dt.datetime.now)
    end_date = models.DateField(null=True)

    class Meta:
        verbose_name_plural = "rules of origin documents"
        unique_together = ("source_url", )

    def __str__(self):
        return self.description


class Rule(models.Model):
    """
    Rule of Origin belonging to a Rules Of Origin Document and related to a commodity object
    """

    code = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    description_processed = models.TextField(null=True, blank=True)
    is_exclusion = models.BooleanField(default=False)
    rules_document = models.ForeignKey(
        "RulesDocument", on_delete=models.CASCADE, null=True, blank=True
    )
    rule_text = models.TextField(null=True, blank=True)
    alt_rule_text = models.TextField(null=True, blank=True)
    rule_text_processed = models.TextField(null=True, blank=True)
    alt_rule_text_processed = models.TextField(null=True, blank=True)

    chapters = models.ManyToManyField(
        "hierarchy.Chapter",
        related_name="rules_of_origin",
    )
    headings = models.ManyToManyField(
        "hierarchy.Heading",
        related_name="rules_of_origin",
    )
    subheadings = models.ManyToManyField(
        "hierarchy.SubHeading",
        related_name="rules_of_origin",
    )
    commodities = models.ManyToManyField(
        "commodities.Commodity",
        related_name="rules_of_origin",
    )

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.description

    @property
    def num_rules(self):
        return 1 + self.subrules.count()

    def get_child_rules(self):
        """
        get child Rules if Chapter level rule
        :return: list of rules
        """
        return [
            rule
            for rule in self.chapter.rules_of_origin.all()
            if self.chapter is not None
        ]

    def get_processed_description(self, country_code):
        return self.description_processed.format(country_code=country_code)

    def get_processed_text(self, country_code):
        return self.rule_text_processed.format(country_code=country_code)

    def get_processed_alt_text(self, country_code):
        return self.alt_rule_text_processed.format(country_code=country_code)


class SubRule(models.Model):
    rule = models.ForeignKey("Rule", on_delete=models.CASCADE, related_name='subrules')
    order = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    description_processed = models.TextField(null=True, blank=True)
    rule_text = models.TextField(null=True, blank=True)
    alt_rule_text = models.TextField(null=True, blank=True)
    rule_text_processed = models.TextField(null=True, blank=True)
    alt_rule_text_processed = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def get_processed_rule(self, country_code):
        return self.rule_text_processed.format(country_code=country_code)

    def get_processed_alt_rule(self, country_code):
        return self.alt_rule_text_processed.format(country_code=country_code)


class RulesDocumentFootnote(models.Model):
    """
    Rules of origin document footnotes
    """

    number = models.PositiveSmallIntegerField()
    identifier = models.TextField(blank=True, null=True)
    link_html = models.TextField(blank=True, null=True)
    note = models.TextField()
    rules_document = models.ForeignKey(
        "RulesDocument", on_delete=models.CASCADE, related_name="footnotes"
    )

    class Meta:
        verbose_name_plural = "rules document footnotes"
        ordering = ["number"]

    def __str__(self):
        return "Footnote {0}".format(self.number)
