from django.db import models

from countries.models import Country


class OldRulesGroup(models.Model):
    """
    Rules of Origin Group
    """

    description = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.description


class OldRulesGroupMember(models.Model):
    """
    Rules of Origin Group
    """

    old_rules_group = models.ForeignKey("OldRulesGroup", on_delete=models.CASCADE)
    country = models.ForeignKey("countries.Country", on_delete=models.CASCADE)
    start_date = models.DateField()
    finish_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "rules of origin group members"
        unique_together = ("country", "old_rules_group", "start_date")

    def __str__(self):
        return "{1} Old rules group member {0}".format(
            self.country.country_code, self.old_rules_group.description
        )


class OldRulesDocument(models.Model):
    """
    Rules Of Origin Document optionally related to a Country Group
    """

    description = models.TextField()
    old_rules_group = models.ForeignKey(
        "OldRulesGroup", on_delete=models.CASCADE, null=True, blank=True
    )
    source_url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "rules of origin documents"
        unique_together = ("old_rules_group", "source_url")

    def __str__(self):
        return self.description


class OldRule(models.Model):
    """
    Rule of Origin belonging to a Rules Of Origin Documents and related to a Commodity Heading Heading
    """

    rule_id = models.CharField(max_length=255)
    is_exclusion = models.BooleanField(default=False)
    old_rules_document = models.ForeignKey(
        "OldRulesDocument", on_delete=models.CASCADE, null=True, blank=True
    )
    chapter = models.ForeignKey(
        "hierarchy.Chapter",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="old_rules_of_origin",
    )

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.rule_id

    def get_child_rules(self):
        """
        get child Rules if Chapter level rule
        :return: list of rules
        """
        return [
            rule
            for rule in self.chapter.old_rules_of_origin.all()
            if self.chapter is not None
        ]


class OldRuleItem(models.Model):
    old_rule = models.ForeignKey("OldRule", on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    working_or_processing = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["order"]


class OldRulesDocumentFootnote(models.Model):
    """
    Rules of origin document footnotes
    """

    number = models.PositiveSmallIntegerField()
    link_html = models.TextField()
    note = models.TextField()
    old_rules_document = models.ForeignKey(
        "OldRulesDocument", on_delete=models.CASCADE, related_name="old_footnotes"
    )

    class Meta:
        verbose_name_plural = "rules document footnotes"

    def __str__(self):
        return "Footnote {0}".format(self.number)


class RulesDocument(models.Model):
    """
    Rules Of Origin Document optionally related to a Country Group
    """

    description = models.TextField()
    countries = models.ManyToManyField(Country, related_name='rules_documents')
    source_url = models.URLField(null=True, blank=True)
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True)

    class Meta:
        verbose_name_plural = "rules of origin documents"
        unique_together = ("source_url", )

    def __str__(self):
        return self.description


class Rule(models.Model):
    """
    Rule of Origin belonging to a Rules Of Origin Documents and related to a Commodity Heading Heading
    """

    code = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    is_exclusion = models.BooleanField(default=False)
    rules_document = models.ForeignKey(
        "RulesDocument", on_delete=models.CASCADE, null=True, blank=True
    )
    rule_text = models.TextField(null=True, blank=True)
    alt_rule_text = models.TextField(null=True, blank=True)
    chapters = models.ManyToManyField(
        "hierarchy.Chapter",
        related_name="rules_of_origin",
    )
    headings = models.ManyToManyField(
        "hierarchy.Heading",
        related_name="rules_of_origin",
    )

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.description

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
    rule = models.ForeignKey("Rule", on_delete=models.CASCADE)
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
