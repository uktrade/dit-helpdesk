import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from commodities.models import Commodity
from hierarchy.models import Chapter, Heading, SubHeading
from regulations.models import Regulation, RegulationGroup

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
    RegulationGroupForm,
    RegulationRemoveForm,
    RegulationSearchForm,
    SubHeadingAddForm,
    SubHeadingAddSearchForm,
    SubHeadingRemoveForm,
)
from .models import Approval


logger = logging.getLogger(__name__)


class BaseCMSMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["pending_approvals_count"] = Approval.objects.pending().count()

        return ctx


class CMSView(BaseCMSMixin, View):
    def get(self, request):
        return redirect("cms:regulation-groups-list")


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
    form_class = RegulationGroupForm
    template_name = "cms/regulations/regulationgroup_create.html"

    def form_valid(self, form):
        deferred_create = form.defer_create()
        regulation_group_title = form.cleaned_data["title"]

        approval = Approval.objects.create(
            created_by=self.request.user,
            deferred_change=deferred_create,
            description=f'Create regulation group "{regulation_group_title}"',
        )

        return redirect("cms:approval-detail", pk=approval.pk)


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
        return self.regulation_group in RegulationGroup.objects.inherited(
            self.commodity_object
        )

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
                SearchResult(regulation_group, obj)
                for obj in self.get_search_results(search_form)
            )

        add_form = self.get_add_form()
        ctx["add_form"] = add_form
        return ctx

    def get_search_form(self):
        return self.search_form_class(self.request.GET)

    def get_add_form(self):
        return self.add_form_class(self.request.POST, instance=self.get_object())

    def get_approval_description(self):
        raise NotImplementedError("`get_approval_description` needs to be implemented.")

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        add_form = self.get_add_form()
        if add_form.is_valid():
            deferred_update = add_form.defer_update()
            approval = Approval.objects.create(
                created_by=self.request.user,
                deferred_change=deferred_update,
                description=self.get_approval_description(),
            )

            return redirect("cms:approval-detail", pk=approval.pk)

        self.object = regulation_group
        ctx = self.get_context_data(object=self.object)
        return self.render_to_response(ctx)

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

    def get_approval_description(self, remove_form):
        raise NotImplementedError("`get_approval_description` needs to be implemented.")

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        remove_form = self.get_remove_form(request.POST)
        if remove_form.is_valid():
            deferred_update = remove_form.defer_update()
            approval = Approval.objects.create(
                created_by=self.request.user,
                deferred_change=deferred_update,
                description=self.get_approval_description(remove_form),
            )

            return redirect("cms:approval-detail", pk=approval.pk)

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
            regulation_form = regulation_form_class(
                initial={"regulation_group": self.get_object()}
            )
        ctx["regulation_form"] = regulation_form

        return ctx

    def get_regulation_form_class(self):
        return RegulationForm

    def post(self, request, *args, **kwargs):
        regulation_form_class = self.get_regulation_form_class()
        regulation_form = regulation_form_class(request.POST)
        if regulation_form.is_valid():
            deferred_create = regulation_form.defer_create()
            regulation_title = regulation_form.cleaned_data["title"]
            regulation_group_title = regulation_form.cleaned_data[
                "regulation_group"
            ].title

            approval = Approval.objects.create(
                created_by=self.request.user,
                deferred_change=deferred_create,
                description=f'Add regulation "{regulation_title}" to "{regulation_group_title}"',
            )
            return redirect("cms:approval-detail", pk=approval.pk)

        self.object = self.get_object()
        ctx = self.get_context_data(object=self.object, regulation_form=regulation_form)
        return self.render_to_response(ctx)


class RegulationGroupRegulationRemoveView(BaseRemoveView):
    selected_panel = "regulations"
    template_name = "cms/regulations/regulationgroup_regulation_remove.html"
    context_object_to_remove_name = "regulation"

    def get_object_to_remove(self):
        return Regulation.objects.get(pk=self.kwargs["regulation_pk"])

    def get_remove_form(self, data=None):
        return RegulationRemoveForm(
            data,
            initial={"regulation": self.get_object_to_remove()},
            instance=self.get_object(),
        )

    def get_approval_description(self, remove_form):
        regulation_group = self.get_object()
        regulation = remove_form.cleaned_data["regulation"]

        return f'Remove "{regulation.title}" from "{regulation_group.title}"'


class RegulationGroupChapterListView(BaseRegulationGroupDetailView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_list.html"


class RegulationGroupChapterAddView(BaseAddView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_add.html"
    search_form_class = ChapterAddSearchForm
    add_form_class = ChapterAddForm

    def get_approval_description(self):
        regulation_group = self.get_object()

        return f'Link chapters to "{regulation_group.title}"'

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

    def get_remove_form(self, data=None):
        return ChapterRemoveForm(
            data,
            initial={"chapter": self.get_object_to_remove()},
            instance=self.get_object(),
        )

    def get_approval_description(self, remove_form):
        regulation_group = self.get_object()
        chapter = remove_form.cleaned_data["chapter"]

        return f'Remove "{regulation_group.title}" from "{chapter.title}"'


class RegulationGroupHeadingListView(BaseRegulationGroupDetailView):
    selected_panel = "headings"
    template_name = "cms/regulations/regulationgroup_heading_list.html"


class RegulationGroupHeadingAddView(BaseAddView):
    selected_panel = "headings"
    template_name = "cms/regulations/regulationgroup_heading_add.html"
    search_form_class = HeadingAddSearchForm
    add_form_class = HeadingAddForm

    def get_approval_description(self):
        regulation_group = self.get_object()

        return f'Link headings to "{regulation_group.title}"'

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

    def get_remove_form(self, data=None):
        return HeadingRemoveForm(
            data,
            initial={"heading": self.get_object_to_remove()},
            instance=self.get_object(),
        )

    def get_approval_description(self, remove_form):
        regulation_group = self.get_object()
        heading = remove_form.cleaned_data["heading"]

        return f'Remove "{regulation_group.title}" from "{heading.description}"'


class RegulationGroupSubHeadingListView(BaseRegulationGroupDetailView):
    selected_panel = "subheadings"
    template_name = "cms/regulations/regulationgroup_subheading_list.html"


class RegulationGroupSubHeadingAddView(BaseAddView):
    selected_panel = "subheadings"
    template_name = "cms/regulations/regulationgroup_subheading_add.html"
    search_form_class = SubHeadingAddSearchForm
    add_form_class = SubHeadingAddForm

    def get_approval_description(self):
        regulation_group = self.get_object()

        return f'Link subheadings to "{regulation_group.title}"'

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

    def get_remove_form(self, data=None):
        return SubHeadingRemoveForm(
            data,
            initial={"subheading": self.get_object_to_remove()},
            instance=self.get_object(),
        )

    def get_approval_description(self, remove_form):
        regulation_group = self.get_object()
        subheading = remove_form.cleaned_data["subheading"]

        return f'Remove "{regulation_group.title}" from "{subheading.description}"'


class RegulationGroupCommodityListView(BaseRegulationGroupDetailView):
    selected_panel = "commodities"
    template_name = "cms/regulations/regulationgroup_commodities_list.html"


class RegulationGroupCommodityAddView(BaseAddView):
    selected_panel = "commodities"
    template_name = "cms/regulations/regulationgroup_commodity_add.html"
    search_form_class = CommodityAddSearchForm
    add_form_class = CommodityAddForm

    def get_approval_description(self):
        regulation_group = self.get_object()

        return f'Link commodities to "{regulation_group.title}"'

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

    def get_remove_form(self, data=None):
        return CommodityRemoveForm(
            data,
            initial={"commodity": self.get_object_to_remove()},
            instance=self.get_object(),
        )

    def get_approval_description(self, remove_form):
        regulation_group = self.get_object()
        commodity = remove_form.cleaned_data["commodity"]

        return f'Remove "{regulation_group.title}"" from "{commodity.description}"'


class PendingApprovalListView(BaseCMSMixin, ListView):
    context_object_name = "pending_approvals"
    model = Approval
    queryset = Approval.objects.pending()
    template_name = "cms/approvals/approval_list.html"


class ApprovalDetailView(BaseCMSMixin, DetailView):
    model = Approval
    template_name = "cms/approvals/approval_detail.html"

    def post(self, request, *args, **kwargs):
        approval = self.get_object()

        if not approval.can_approve(self.request.user):
            raise PermissionDenied

        form, _ = approval.approve(request.user)

        return HttpResponseRedirect(form.get_post_approval_url())

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        approval = self.get_object()
        ctx["form"] = approval.get_bound_form()
        ctx["is_approved"] = approval.approved
        ctx["can_approve"] = approval.can_approve(self.request.user)
        ctx["approval_url"] = self.request.build_absolute_uri()

        return ctx
