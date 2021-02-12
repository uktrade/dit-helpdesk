from django import forms
from django.core.validators import RegexValidator

from hierarchy.models import NomenclatureTree
from regulations.models import (
    Regulation,
    RegulationGroup,
)


class RegulationGroupForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["title"]

    def _save_m2m(self):
        super()._save_m2m()
        self.instance.nomenclature_trees.add(NomenclatureTree.get_active_tree())


class RegulationSearchForm(forms.Form):
    q = forms.CharField(label="Search regulations")


class RegulationForm(forms.ModelForm):
    class Meta:
        model = Regulation
        fields = ["title", "url"]

    url = forms.URLField(
        label="URL",
        validators=[
            RegexValidator(
                Regulation.VALID_URL_REGEX,
                "Invalid legislation URL."
            ),
        ],
    )

    def __init__(self, regulation_group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.regulation_group = regulation_group

    def save(self, commit=True):
        instance = super().save(commit)

        if commit:
            self.regulation_group.regulation_set.add(self.instance)

        return instance


class RegulationRemoveForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = []

    def __init__(self, *args, regulation, **kwargs):
        super().__init__(*args, **kwargs)

        self.regulation = regulation

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.regulation_set.remove(self.regulation)

        return instance


class ChapterAddSearchForm(forms.Form):
    chapter_codes = forms.CharField(
        label="Search chapters",
        help_text="Comma separated list of chapter codes e.g. 01,2100000000,82 (both 2 and 10 digits accepted)",
    )

    def clean_chapter_codes(self):
        chapter_codes = self.cleaned_data["chapter_codes"]

        return [code.strip().ljust(10, "0") for code in chapter_codes.split(",")]


class ChapterAddForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["chapters"]

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.chapters.add(*self.cleaned_data["chapters"])

        return instance


class ChapterRemoveForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = []

    def __init__(self, *args, chapter, **kwargs):
        super().__init__(*args, **kwargs)

        self.chapter = chapter

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.chapters.remove(self.chapter)

        return instance


class HeadingAddSearchForm(forms.Form):
    heading_codes = forms.CharField(
        label="Search headings",
        help_text="Comma separated list of heading codes e.g. 0101,2101000000,8220 (both 4 and 10 digits accepted)",
    )

    def clean_heading_codes(self):
        heading_codes = self.cleaned_data["heading_codes"]

        return [code.strip().ljust(10, "0") for code in heading_codes.split(",")]


class HeadingAddForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["headings"]

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.headings.add(*self.cleaned_data["headings"])

        return instance


class HeadingRemoveForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = []

    def __init__(self, *args, heading, **kwargs):
        super().__init__(*args, **kwargs)

        self.heading = heading

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.headings.remove(self.heading)

        return instance


class SubHeadingAddSearchForm(forms.Form):
    subheading_codes = forms.CharField(
        label="Search subheadings",
        help_text="Comma separated list of subheading codes e.g. 010101,2101220000,822020 (6, 8 and 10 digits accepted)",
    )

    def clean_subheading_codes(self):
        subheading_codes = self.cleaned_data["subheading_codes"]

        return [code.strip().ljust(10, "0") for code in subheading_codes.split(",")]


class SubHeadingAddForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["subheadings"]

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.subheadings.add(*self.cleaned_data["subheadings"])

        return instance


class SubHeadingRemoveForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = []

    def __init__(self, *args, subheading, **kwargs):
        super().__init__(*args, **kwargs)

        self.subheading = subheading

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.subheadings.remove(self.subheading)

        return instance


class CommodityAddSearchForm(forms.Form):
    commodity_codes = forms.CharField(
        label="Search commodities",
        help_text="Comma separated list of subheading codes e.g. 010101,2101220000,822020 (6, 8 and 10 digits accepted)",
    )

    def clean_commodity_codes(self):
        commodity_codes = self.cleaned_data["commodity_codes"]

        return [code.strip().ljust(10, "0") for code in commodity_codes.split(",")]


class CommodityAddForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["commodities"]

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.commodities.add(*self.cleaned_data["commodities"])

        return instance


class CommodityRemoveForm(forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = []

    def __init__(self, *args, commodity, **kwargs):
        super().__init__(*args, **kwargs)

        self.commodity = commodity

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.commodities.remove(self.commodity)

        return instance
