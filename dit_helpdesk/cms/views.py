from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView

from hierarchy.models import Chapter
from regulations.models import RegulationGroup

from .forms import (
    ChapterAddForm,
    ChapterAddSearchForm,
    ChapterRemoveForm,
    RegulationForm,
    RegulationSearchForm,
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


class BaseRegulationGroupDetailView(BaseCMSMixin, DetailView):
    model = RegulationGroup

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        try:
            ctx["selected_panel"] = self.selected_panel
        except AttributeError:
            raise NotImplementedError("Specify a `selected_panel`.")

        return ctx


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


class RegulationGroupChapterListView(BaseRegulationGroupDetailView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_list.html"


class RegulationGroupChapterAddView(BaseRegulationGroupDetailView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_add.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        search_form = self.get_search_form()
        ctx["search_form"] = search_form
        ctx["searching"] = False
        ctx["search_results"] = None

        if self.request.GET and search_form.is_valid():
            ctx["searching"] = True
            ctx["search_results"] = self.get_search_results(search_form)

        add_form = self.get_add_form()
        ctx["add_form"] = add_form

        return ctx

    def get_search_form(self):
        return ChapterAddSearchForm(self.request.GET)

    def get_add_form(self):
        return ChapterAddForm(self.request.POST, instance=self.get_object())

    def get_search_results(self, search_form):
        chapter_codes = search_form.cleaned_data["chapter_codes"]
        chapters = Chapter.objects.filter(chapter_code__in=chapter_codes)

        return chapters

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        add_form = self.get_add_form()
        if add_form.is_valid():
            add_form.save()

            return redirect(
                "cms:regulation-group-chapter-list",
                pk=regulation_group.pk,
            )

        self.object = regulation_group
        ctx = self.get_context_data(object=self.object)
        return self.render_to_response(ctx)


class RegulationGroupChapterRemoveView(BaseRegulationGroupDetailView):
    selected_panel = "chapters"
    template_name = "cms/regulations/regulationgroup_chapter_remove.html"

    def get_chapter(self):
        return Chapter.objects.get(pk=self.kwargs["chapter_pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["chapter"] = self.get_chapter()
        ctx["remove_form"] = self.get_remove_form()

        return ctx

    def get_remove_form(self):
        return ChapterRemoveForm(
            self.request.POST,
            instance=self.get_object(),
            chapter=self.get_chapter(),
        )

    def post(self, request, *args, **kwargs):
        regulation_group = self.get_object()

        remove_form = self.get_remove_form()
        if remove_form.is_valid():
            remove_form.save()

            return redirect(
                "cms:regulation-group-chapter-list",
                pk=regulation_group.pk,
            )

        self.object = regulation_group
        ctx = self.get_context_data(object=self.object)
        return self.render_to_response(ctx)
