from django import forms
from django.core.validators import RegexValidator
from django.urls import reverse

from commodities.models import Commodity
from deferred_changes.forms import DeferredFormMixin
from hierarchy.models import Chapter, Heading, NomenclatureTree, SubHeading
from regulations.models import Regulation, RegulationGroup


class RegulationGroupForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["title"]

    def _save_m2m(self):
        super()._save_m2m()
        self.instance.nomenclature_trees.add(NomenclatureTree.get_active_tree())

    def get_post_approval_url(self):
        return reverse("cms:regulation-group-detail", kwargs={"pk": self.instance.pk})


class RegulationSearchForm(forms.Form):
    q = forms.CharField(label="Search regulations")


class RegulationGroupChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class RegulationForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = Regulation
        fields = ["regulation_group", "title", "url"]

    regulation_group = RegulationGroupChoiceField(
        queryset=RegulationGroup.objects.all(), widget=forms.HiddenInput
    )
    url = forms.URLField(
        label="URL",
        validators=[
            RegexValidator(Regulation.VALID_URL_REGEX, "Invalid legislation URL.")
        ],
    )

    def _save_m2m(self):
        super()._save_m2m()
        regulation_group = self.cleaned_data["regulation_group"]
        self.instance.regulation_groups.add(regulation_group)
        self.instance.nomenclature_trees.add(NomenclatureTree.get_active_tree())

    def get_post_approval_url(self):
        regulation_group = self.cleaned_data["regulation_group"]

        return reverse(
            "cms:regulation-group-detail", kwargs={"pk": regulation_group.pk}
        )


class RegulationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class RegulationRemoveForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["regulation"]

    regulation = RegulationChoiceField(
        queryset=Regulation.objects.all(), widget=forms.HiddenInput
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.regulation_set.remove(self.cleaned_data["regulation"])

        return instance

    def get_post_approval_url(self):
        return reverse("cms:regulation-group-detail", kwargs={"pk": self.instance.pk})


class ChapterAddSearchForm(forms.Form):
    chapter_codes = forms.CharField(
        label="Search chapters",
        help_text="Comma separated list of chapter codes e.g. 01,2100000000,82 (both 2 and 10 digits accepted)",
    )

    def clean_chapter_codes(self):
        chapter_codes = self.cleaned_data["chapter_codes"]

        return [code.strip().ljust(10, "0") for code in chapter_codes.split(",")]


class ChapterLabelFromInstanceMixin:
    def label_from_instance(self, obj):
        return f"{obj.description} ({obj.chapter_code})"


class ChapterModelMultipleChoiceField(
    ChapterLabelFromInstanceMixin, forms.ModelMultipleChoiceField
):
    pass


class ChapterAddForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["chapters"]

    chapters = ChapterModelMultipleChoiceField(
        queryset=Chapter.objects.all(), to_field_name="goods_nomenclature_sid"
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.chapters.add(*self.cleaned_data["chapters"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-chapter-list", kwargs={"pk": self.instance.pk}
        )


class ChapterChoiceField(ChapterLabelFromInstanceMixin, forms.ModelChoiceField):
    pass


class ChapterRemoveForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["chapter"]

    chapter = ChapterChoiceField(
        queryset=Chapter.objects.all(),
        to_field_name="goods_nomenclature_sid",
        widget=forms.HiddenInput,
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.chapters.remove(self.cleaned_data["chapter"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-chapter-list", kwargs={"pk": self.instance.pk}
        )


class HeadingAddSearchForm(forms.Form):
    heading_codes = forms.CharField(
        label="Search headings",
        help_text="Comma separated list of heading codes e.g. 0101,2101000000,8220 (both 4 and 10 digits accepted)",
    )

    def clean_heading_codes(self):
        heading_codes = self.cleaned_data["heading_codes"]

        return [code.strip().ljust(10, "0") for code in heading_codes.split(",")]


class HeadingLabelFromInstanceMixin:
    def label_from_instance(self, obj):
        return f"{obj.description} ({obj.heading_code})"


class HeadingModelMultipleChoiceField(
    HeadingLabelFromInstanceMixin, forms.ModelMultipleChoiceField
):
    pass


class HeadingAddForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["headings"]

    headings = HeadingModelMultipleChoiceField(
        queryset=Heading.objects.all(), to_field_name="goods_nomenclature_sid"
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.headings.add(*self.cleaned_data["headings"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-heading-list", kwargs={"pk": self.instance.pk}
        )


class HeadingChoiceField(HeadingLabelFromInstanceMixin, forms.ModelChoiceField):
    pass


class HeadingRemoveForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["heading"]

    heading = HeadingChoiceField(
        queryset=Heading.objects.all(),
        to_field_name="goods_nomenclature_sid",
        widget=forms.HiddenInput,
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.headings.remove(self.cleaned_data["heading"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-heading-list", kwargs={"pk": self.instance.pk}
        )


class SubHeadingAddSearchForm(forms.Form):
    subheading_codes = forms.CharField(
        label="Search subheadings",
        help_text="Comma separated list of subheading codes e.g. 010101,2101220000,822020 (6, 8 and 10 digits accepted)",  # noqa: E501
    )

    def clean_subheading_codes(self):
        subheading_codes = self.cleaned_data["subheading_codes"]

        return [code.strip().ljust(10, "0") for code in subheading_codes.split(",")]


class SubHeadingLabelFromInstanceMixin:
    def label_from_instance(self, obj):
        return f"{obj.description} ({obj.commodity_code})"


class SubHeadingModelMultipleChoiceField(
    SubHeadingLabelFromInstanceMixin, forms.ModelMultipleChoiceField
):
    pass


class SubHeadingAddForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["subheadings"]

    subheadings = SubHeadingModelMultipleChoiceField(
        queryset=SubHeading.objects.all(), to_field_name="goods_nomenclature_sid"
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.subheadings.add(*self.cleaned_data["subheadings"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-subheading-list", kwargs={"pk": self.instance.pk}
        )


class SubHeadingChoiceField(SubHeadingLabelFromInstanceMixin, forms.ModelChoiceField):
    pass


class SubHeadingRemoveForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["subheading"]

    subheading = SubHeadingChoiceField(
        queryset=SubHeading.objects.all(),
        to_field_name="goods_nomenclature_sid",
        widget=forms.HiddenInput,
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.subheadings.remove(self.cleaned_data["subheading"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-subheading-list", kwargs={"pk": self.instance.pk}
        )


class CommodityAddSearchForm(forms.Form):
    commodity_codes = forms.CharField(
        label="Search commodities",
        help_text="Comma separated list of subheading codes e.g. 010101,2101220000,822020 (6, 8 and 10 digits accepted)",  # noqa: E501
    )

    def clean_commodity_codes(self):
        commodity_codes = self.cleaned_data["commodity_codes"]

        return [code.strip().ljust(10, "0") for code in commodity_codes.split(",")]


class CommodityLabelFromInstanceMixin:
    def label_from_instance(self, obj):
        return f"{obj.description} ({obj.commodity_code})"


class CommodityModelMultipleChoiceField(
    CommodityLabelFromInstanceMixin, forms.ModelMultipleChoiceField
):
    pass


class CommodityAddForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["commodities"]

    commodities = CommodityModelMultipleChoiceField(
        queryset=Commodity.objects.all(), to_field_name="goods_nomenclature_sid"
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.commodities.add(*self.cleaned_data["commodities"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-commodity-list", kwargs={"pk": self.instance.pk}
        )


class CommodityModelChoiceField(
    CommodityLabelFromInstanceMixin, forms.ModelChoiceField
):
    pass


class CommodityRemoveForm(DeferredFormMixin, forms.ModelForm):
    class Meta:
        model = RegulationGroup
        fields = ["commodity"]

    commodity = CommodityModelChoiceField(
        queryset=Commodity.objects.all(),
        to_field_name="goods_nomenclature_sid",
        widget=forms.HiddenInput,
    )

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()
            instance.commodities.remove(self.cleaned_data["commodity"])

        return instance

    def get_post_approval_url(self):
        return reverse(
            "cms:regulation-group-commodity-list", kwargs={"pk": self.instance.pk}
        )
