from django.db import models


class RulesGroup(models.Model):
    """
    Rules of Origin Group
    """
    description = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.description


class RulesGroupMember(models.Model):
    """
    Rules of Origin Group
    """
    rules_group = models.ForeignKey("RulesGroup", on_delete=models.CASCADE)
    country = models.ForeignKey("countries.Country", on_delete=models.CASCADE)
    start_date = models.DateField()
    finish_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "rules of origin group members"
        unique_together = ('country', 'rules_group', 'start_date')

    def __str__(self):
        return "{1} Rules group member {0}".format(self.country.country_code, self.rules_group.description)


class RulesDocument(models.Model):
    """
    Rules Of Origin Document optionally related to a Country Group
    """
    description = models.TextField()
    rules_group = models.ForeignKey("RulesGroup", on_delete=models.CASCADE, null=True, blank=True)
    source_url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "rules of origin documents"
        unique_together = ('rules_group', 'source_url')

    def __str__(self):
        return self.description


class Rule(models.Model):
    """
    Rule of Origin belonging to a Rules Of Origin Documents and related to a Commodity Heading Heading
    """
    rule_id = models.CharField(max_length=255)
    description = models.TextField()
    working_or_processing_one = models.TextField(null=True, blank=True)
    working_or_processing_two = models.TextField(null=True, blank=True)
    is_exclusion = models.BooleanField(default=False)
    rules_document = models.ForeignKey("RulesDocument", on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey("hierarchy.Chapter", on_delete=models.CASCADE, null=True, blank=True,
                                related_name="rules_of_origin")

    class Meta:
        verbose_name_plural = "rules of origin"

    def __str__(self):
        return self.description

    def get_child_rules(self):
        """
        get child Rules if Chapter level rule
        :return: list of rules
        """
        return [rule for rule in self.chapter.rules_of_origin.all() if self.chapter is not None]


class RulesDocumentFootnote(models.Model):
    """
    Rules of origin document footnotes
    """
    number = models.PositiveSmallIntegerField()
    link_html = models.TextField()
    note = models.TextField()
    rules_document = models.ForeignKey("RulesDocument", on_delete=models.CASCADE, related_name="footnotes")

    class Meta:
        verbose_name_plural = "rules document footnotes"

    def __str__(self):
        return "Footnote {0}".format(self.number)