from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from commodities.models import Commodity
from hierarchy.models import (
    Chapter,
    Heading,
    SubHeading,
)
from regulations.models import (
    Regulation,
    RegulationGroup,
)

from .forms import (
    ChapterAddForm,
    ChapterAddSearchForm,
    ChapterRemoveForm,
    CommodityAddForm,
    CommodityAddSearchForm,
    CommodityRemoveForm,
    HeadingAddForm,
    HeadingAddSearchForm,
    HeadingRemoveForm,
    RegulationForm,
    RegulationRemoveForm,
    RegulationSearchForm,
    SubHeadingAddForm,
    SubHeadingAddSearchForm,
    SubHeadingRemoveForm,
)


class BaseCMSMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CMSView(BaseCMSMixin, View):

    def get(self, request):
        return HttpResponse("OK")


class RegulationGroupsListView(BaseCMSMixin, ListView):
    model = RegulationGroup
    paginate_by = 10
    template_name = "cms/regulations/regulationgroup_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        search_form = self.get_search_form()
        ctx["search_form"] = search_form
        ctx["searching"] = False
        ctx["search_query"] = None

        if self.request.GET and search_form.is_valid():
            ctx["searching"] = True
            ctx["search_query"] = search_form.cleaned_data.get("q")

        return ctx

    def get_search_form(self):
        return RegulationSearchForm(self.request.GET)

    def get_queryset(self):
        queryset = super().get_queryset().order_by("title")

        search_form = self.get_search_form()
        if search_form.is_valid():
            search_query = search_form.cleaned_data.get("q")
            queryset = queryset.filter(title__search=search_query)

        return queryset


class RegulationGroupCreateView(BaseCMSMixin, CreateView):
    fields = ["title"]
    model = RegulationGroup
    template_name = "cms/regulations/regulationgroup_create.html"

    def get_success_url(self):
        return reverse(
            "cms:regulation-group-detail",
            kwargs={
                "pk": self.object.pk,
            },
        )


class BaseRegulationGroupDetailView(BaseCMSMixin, DetailView):
    model = RegulationGroup

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        try:
            ctx["selected_panel"] = self.selected_panel
        except AttributeError:
            raise NotImplementedError("Specify a `selected_panel`.")

        return ctx


class SearchResult:
    def __init__(self, regulation_group, commodity_object):
        self.regulation_group = regulation_group
        self.commodity_object = commodity_object

    def is_already_associated(self):
        return self.regulation_group in RegulationGroup.objects.inherited(self.commodity_object)

    def __getattr__(self, attr):
        return getattr(self.commodity_object, attr)


class BaseAddView(BaseRegulationGroupDetailView):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        search_form = self.get_search_form()
        ctx["search_form"] = search_form
        ctx["searching"] = False
        ctx["search_results"] = None

        if self.request.GET and search_form.is_valid():
            ctx["searching"] = True
            regulation_group = self.get_object()
            ctx["search_results"] = (
                SearchResult(regulation_group, obj) for obj in self.get_search_results(search_form)
            )

        add_form = self.get_add_form()
        ctx["add_form"] = add_form

        return ctx

    def get_search_form(self):
        return self.search_form_class(self.request.GET)

    def get_add_form(self):
        return self.add_form_class(self.request.POST, instance=self.get_object())

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        add_form = self.get_add_form()
        if add_form.is_valid():
            add_form.save()

            return redirect(self.get_success_url())

        self.object = regulation_group
        ctx = self.get_context_data(object=self.object)
        return self.render_to_response(ctx)

    def get_success_url(self):
        raise NotImplementedError("`get_success_url` needs to be implemented.")

    def get_search_results(self, search_form):
        raise NotImplementedError("`get_search_results` needs to be implemented.")


class BaseRemoveView(BaseRegulationGroupDetailView):
    def get_object_to_remove(self):
        raise NotImplementedError("`get_object_to_remove` needs to be implemented.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx[self.context_object_to_remove_name] = self.get_object_to_remove()
        ctx["remove_form"] = self.get_remove_form()

        return ctx

    def get_remove_form(self):
        raise NotImplementedError("`get_remove_form` needs to be implemented.")

    def get_success_url(self):
        raise NotImplementedError("`get_success_url` needs to be implemented.")

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        remove_form = self.get_remove_form()
        if remove_form.is_valid():
            remove_form.save()

            return redirect(self.get_success_url())

        self.object = regulation_group
        ctx = self.get_context_data(object=self.object)
        return self.render_to_response(ctx)


class RegulationGroupDetailView(BaseRegulationGroupDetailView):
    selected_panel = "regulations"
    template_name = "cms/regulations/regulationgroup_detail.html"


class RegulationGroupRegulationCreateView(BaseRegulationGroupDetailView):
    selected_panel = "regulations"
    template_name = "cms/regulations/regulationgroup_regulation_create.html"

    def get_context_data(self, regulation_form=None, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if not regulation_form:
            regulation_form_class = self.get_regulation_form_class()
            regulation_form = regulation_form_class(self.get_object())
        ctx["regulation_form"] = regulation_form

        return ctx

    def get_regulation_form_class(self):
        return RegulationForm

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        regulation_form_class = self.get_regulation_form_class()
        regulation_form = regulation_form_class(regulation_group, request.POST)
        if regulation_form.is_valid():
            regulation_form.save()
            return redirect(
                "cms:regulation-group-detail",
                pk=regulation_group.pk,
            )

        self.object = self.get_object()
        ctx = self.get_context_data(object=self.object, regulation_form=regulation_form)
        return self.render_to_response(ctx)


class RegulationGroupRegulationRemoveView(BaseRemoveView):
    selected_panel = "regulations"
    template_name = "cms/regulations/regulationgroup_regulation_remove.html"
    context_object_to_remove_name = "regulation"

    def get_object_to_remove(self):
        return Regulation.objects.get(pk=self.kwargs["regulation_pk"])

    def get_remove_form(self):
        return RegulationRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            regulation=self.get_object_to_remove(),
        )

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-detail",
            kwargs={
                "pk": regulation_group.pk,
            },
        )


class RegulationGroupChapterListView(BaseRegulationGroupDetailView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_list.html"


class RegulationGroupChapterAddView(BaseAddView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_add.html"
    search_form_class = ChapterAddSearchForm
    add_form_class = ChapterAddForm

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-chapter-list",
            kwargs={
                'pk': regulation_group.pk,
            },
        )

    def get_search_results(self, search_form):
        chapter_codes = search_form.cleaned_data["chapter_codes"]
        chapters = Chapter.objects.filter(chapter_code__in=chapter_codes)

        return chapters


class RegulationGroupChapterRemoveView(BaseRemoveView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_remove.html"
    context_object_to_remove_name = "chapter"

    def get_object_to_remove(self):
        return Chapter.objects.get(pk=self.kwargs["chapter_pk"])

    def get_remove_form(self):
        return ChapterRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            chapter=self.get_object_to_remove(),
        )

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-chapter-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )


class RegulationGroupHeadingListView(BaseRegulationGroupDetailView):
    selected_panel = "headings"
    template_name = "cms/regulations/regulationgroup_heading_list.html"


class RegulationGroupHeadingAddView(BaseAddView):
    selected_panel = "headings"
    template_name = "cms/regulations/regulationgroup_heading_add.html"
    search_form_class = HeadingAddSearchForm
    add_form_class = HeadingAddForm

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-heading-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )

    def get_search_results(self, search_form):
        heading_codes = search_form.cleaned_data["heading_codes"]
        headings = Heading.objects.filter(heading_code__in=heading_codes)

        return headings


class RegulationGroupHeadingRemoveView(BaseRemoveView):
    selected_panel = "headings"
    template_name = "cms/regulations/regulationgroup_heading_remove.html"
    context_object_to_remove_name = "heading"

    def get_object_to_remove(self):
        return Heading.objects.get(pk=self.kwargs["heading_pk"])

    def get_remove_form(self):
        return HeadingRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            heading=self.get_object_to_remove(),
        )

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-heading-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )


class RegulationGroupSubHeadingListView(BaseRegulationGroupDetailView):
    selected_panel = "subheadings"
    template_name = "cms/regulations/regulationgroup_subheading_list.html"


class RegulationGroupSubHeadingAddView(BaseAddView):
    selected_panel = "subheadings"
    template_name = "cms/regulations/regulationgroup_subheading_add.html"
    search_form_class = SubHeadingAddSearchForm
    add_form_class = SubHeadingAddForm

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-subheading-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )

    def get_search_results(self, search_form):
        subheading_codes = search_form.cleaned_data["subheading_codes"]
        subheadings = SubHeading.objects.filter(commodity_code__in=subheading_codes)

        return subheadings


class RegulationGroupSubHeadingRemoveView(BaseRemoveView):
    selected_panel = "subheadings"
    template_name = "cms/regulations/regulationgroup_subheading_remove.html"
    context_object_to_remove_name = "subheading"

    def get_object_to_remove(self):
        return SubHeading.objects.get(pk=self.kwargs["subheading_pk"])

    def get_remove_form(self):
        return SubHeadingRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            subheading=self.get_object_to_remove(),
        )

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-subheading-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )


class RegulationGroupCommodityListView(BaseRegulationGroupDetailView):
    selected_panel = "commodities"
    template_name = "cms/regulations/regulationgroup_commodities_list.html"


class RegulationGroupCommodityAddView(BaseAddView):
    selected_panel = "commodities"
    template_name = "cms/regulations/regulationgroup_commodity_add.html"
    search_form_class = CommodityAddSearchForm
    add_form_class = CommodityAddForm

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-commodity-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )

    def get_search_results(self, search_form):
        commodity_codes = search_form.cleaned_data["commodity_codes"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_codes)

        return commodities


class RegulationGroupCommodityRemoveView(BaseRemoveView):
    selected_panel = "commodities"
    template_name = "cms/regulations/regulationgroup_commodities_remove.html"
    context_object_to_remove_name = "commodity"

    def get_object_to_remove(self):
        return Commodity.objects.get(pk=self.kwargs["commodity_pk"])

    def get_remove_form(self):
        return CommodityRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            commodity=self.get_object_to_remove(),
        )

    def get_success_url(self):
        regulation_group = self.get_object()

        return reverse(
            "cms:regulation-group-commodity-list",
            kwargs={
                "pk": regulation_group.pk,
            },
        )
