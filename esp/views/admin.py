from django.db.models import Max
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from common.constants import PermissionType
from common.forms import CrispyFormsetHelper
from esp.auth import PermissionRequiredMixin
from esp.forms import (CourseForm, ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm)
from esp.models.program import Course, Program, ProgramStage


class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.programs_edit
    model = Program
    form_class = ProgramForm

    def get_success_url(self):
        return reverse_lazy('create_program_stage', kwargs={"pk": self.object.id})


class ProgramUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.programs_edit
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('programs')

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["submit_label"] = "Update Program"
        return form_kwargs


class ProgramListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.programs_view_all
    model = Program


class ProgramStageFormsetMixin:
    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data()
        context["step_formset"] = ProgramRegistrationStepFormset()
        context["step_formset_helper"] = CrispyFormsetHelper()
        return context

    def get_formset_kwargs(self):
        if self.program_stage:
            return {"instance": self.program_stage.program}

    def post(self, request, *args, **kwargs):
        redirect_link = super().post(request, *args, **kwargs)
        if self.program_stage:
            step_formset = ProgramRegistrationStepFormset(request.POST, instance=self.program_stage)
            if step_formset.is_valid():
                step_formset.save()
        return redirect_link


class ProgramStageCreateView(PermissionRequiredMixin, SingleObjectMixin, ProgramStageFormsetMixin, FormView):
    permission = PermissionType.programs_edit
    model = Program
    form_class = ProgramStageForm
    template_name = "esp/program_stage_form.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.program_stage = None
        self.object = None

    def get_success_url(self):
        if self.request.POST.get("save-add-new"):
            return reverse_lazy("create_program_stage", kwargs={"pk": self.object.id})
        return reverse_lazy("programs")

    def form_valid(self, form):
        self.object = self.get_object()
        max_index = self.object.stages.aggregate(Max('index'))["index__max"]
        if max_index:
            form.instance.index = max_index + 1
        form.instance.program = self.object
        self.program_stage = form.save()
        return redirect(self.get_success_url())


class ProgramStageUpdateView(PermissionRequiredMixin, ProgramStageFormsetMixin, UpdateView):
    permission = PermissionType.programs_edit
    model = ProgramStage
    form_class = ProgramStageForm
    context_object_name = "stage"
    template_name = "esp/program_stage_form.html"
    success_url = reverse_lazy("programs")

    def get_object(self, queryset=None):
        self.program_stage = super().get_object(queryset)
        return self.program_stage

###########################################################


class CourseCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.courses_edit
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy('programs')


class CourseUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.courses_edit
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy('programs')


class CourseListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.courses_view_all
    model = Course
