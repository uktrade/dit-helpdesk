import datetime as dt

from django.db import models

from countries.models import Country


class RulesDocument(models.Model):
    """
    Rules Of Origin Document optionally related to a Country Group
    """

    description = models.TextField()
    countries = models.ManyToManyField(Country, related_name="rules_documents")
    source_url = models.URLField(null=True, blank=True)
    start_date = models.DateField(default=dt.datetime.now)
    end_date = models.DateField(null=True)

    class Meta:
        verbose_name_plural = "rules of origin documents"
        unique_together = ("source_url",)

    def __str__(self):
        return self.description


MAX_RULES_CODE_DIGITS = 6


class Rule(models.Model):
    """
    Rule of Origin belonging to a Rules Of Origin Document
    """

    code = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_exclusion = models.BooleanField(default=False)
    rules_document = models.ForeignKey(
        "RulesDocument", on_delete=models.CASCADE, null=True, blank=True
    )
    rule_text = models.TextField(null=True, blank=True)
    alt_rule_text = models.TextField(null=True, blank=True)
    hs_from = models.CharField(null=True, max_length=MAX_RULES_CODE_DIGITS)
    hs_from_type = models.CharField(null=True, max_length=2)
    hs_to = models.CharField(null=True, max_length=MAX_RULES_CODE_DIGITS)
    hs_to_type = models.CharField(null=True, max_length=2)

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return f"{self.rules_document} - {self.code}"

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


class SubRule(models.Model):
    rule = models.ForeignKey("Rule", on_delete=models.CASCADE, related_name="subrules")
    order = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    rule_text = models.TextField(null=True, blank=True)
    alt_rule_text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["order"]


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
