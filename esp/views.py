from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, FormView, UpdateView

from common.forms import CrispyFormsetHelper
from esp.forms import (CourseForm, ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, RegisterUserForm)
from esp.models import Course, Program, ProgramRegistration, ProgramStage


class RegisterAccountView(CreateView):
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


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy('programs')


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy('programs')


class CourseListView(ListView):
    model = Course


###########################################################
class BaseDashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TeacherDashboardView(BaseDashboardView):
    template_name = 'dashboards/teacher_dashboard.html'


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboards/admin_dashboard.html'


class StudentDashboardView(BaseDashboardView):
    template_name = 'dashboards/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_registrations = self.request.user.registrations.all()
        context["registrations"] = user_registrations
        # TODO: add eligible program logic once student profile model exists
        context["eligible_programs"] = Program.objects.exclude(id__in=user_registrations.values("program_id"))
        return context


class GuardianDashboardView(BaseDashboardView):
    template_name = 'dashboards/guardian_dashboard.html'


#######################################################
class ProgramRegistrationView(SingleObjectMixin, View):
    model = Program

    def get(self, request, *args, **kwargs):
        program = self.get_object()
        ProgramRegistration.objects.get_or_create(
            program=program, user=self.request.user, defaults={"stage": program.stages.first()}
        )
        return redirect(reverse("current_registration_step", kwargs={"pk": program.id}))


class PreferenceEntryView(DetailView):
    model = Program
    context_object_name = "program"
    template_name = 'esp/class_preference_entry.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration"] = get_object_or_404(
            ProgramRegistration, program_id=self.object.id, user=self.request.user
        )
        return context
