from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, FormView, UpdateView

from common.forms import CrispyFormsetHelper
from esp.forms import (ClassForm, ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, RegisterUserForm)
from esp.models import Course, Program, ProgramStage


class RegisterView(CreateView):
    template_name = "registration.html"
    form_class = RegisterUserForm
    success_url = reverse_lazy('index')

###########################################################


class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm

    def get_success_url(self):
        return reverse_lazy('create_program_stage', kwargs={"pk": self.object.id})


class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('programs')

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["submit_label"] = "Update Program"
        return form_kwargs


class ProgramListView(ListView):
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


class ProgramStageCreateView(SingleObjectMixin, ProgramStageFormsetMixin, FormView):
    model = Program
    context_object_name = "program"
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


class ProgramStageUpdateView(ProgramStageFormsetMixin, UpdateView):
    model = ProgramStage
    form_class = ProgramStageForm
    context_object_name = "stage"
    template_name = "esp/program_stage_form.html"
    success_url = reverse_lazy("programs")

    def get_object(self, queryset=None):
        self.program_stage = super().get_object(queryset)
        return self.program_stage


###########################################################


class ClassCreateView(CreateView):
    model = Course
    form_class = ClassForm
    success_url = reverse_lazy('programs')


class ClassUpdateView(UpdateView):
    model = Course
    form_class = ClassForm
    success_url = reverse_lazy('programs')


class ClassListView(ListView):
    model = Course


###########################################################
class BaseDashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TeacherDashboardView(BaseDashboardView):
    template_name = 'esp/teacher_dashboard.html'


class AdminDashboardView(BaseDashboardView):
    template_name = 'esp/admin_dashboard.html'


class StudentDashboardView(BaseDashboardView):
    template_name = 'esp/student_dashboard.html'


class GuardianDashboardView(BaseDashboardView):
    template_name = 'esp/guardian_dashboard.html'
