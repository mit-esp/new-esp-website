from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, FormView, ListView, TemplateView,
                                  UpdateView)
from django.views.generic.detail import SingleObjectMixin

from common.constants import PermissionType, UserType
from common.forms import CrispyFormsetHelper
from common.models import User
from common.views import PermissionRequiredMixin
from esp.constants import StudentRegistrationStepType
from esp.forms import (ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, TeacherCourseForm)
from esp.lottery import run_program_lottery
from esp.models.program import Course, Program, ProgramStage
######################################
# ADMIN DASHBOARD
######################################
from esp.models.program_registration import ClassRegistration


class AdminDashboardView(TemplateView):
    permission = PermissionType.admin_dashboard_view
    template_name = 'esp/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        ts = timezone.now()
        context["users_count"] = User.objects.count()
        context["students_count"] = User.objects.filter(user_type=UserType.student).count()
        context["teachers_count"] = User.objects.filter(user_type=UserType.teacher).count()
        context["admins_count"] = User.objects.filter(user_type=UserType.admin, is_active=True).count()
        context["upcoming_program"] = Program.objects.filter(start_date__gte=ts).latest('-start_date', '-end_date')
        context["active_programs"] = Program.objects.filter(start_date__lte=ts, end_date__gte=ts).order_by('-start_date')
        return context

class AdminManageStudentsView(TemplateView):
    permission = PermissionType.admin_dashboard_view
    template_name = 'esp/manage_students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        StudentRegistrationStepType
        context["StudentRegistrationStepType"] = StudentRegistrationStepType
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        students = User.objects.filter(user_type=UserType.student, registrations__program=program).select_related('student_profile')
        context["students"] = ["%s %s (%s)" % (u.first_name, u.last_name, u.username) for u in students]
        return context

class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.programs_edit_all
    model = Program
    form_class = ProgramForm

    def form_valid(self, form):
        next_link = super().form_valid(form)
        return next_link

    def get_success_url(self):
        return reverse_lazy('create_program_stage', kwargs={"pk": self.object.id})


class ProgramUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.programs_edit_all
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('programs')

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["submit_label"] = "Update Program"
        return form_kwargs


class ProgramListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.programs_view_all
    context_object_name = "data"
    template_name = "esp/program_list.html"

    def get_queryset(self):
        data = {
            "upcoming_programs": Program.objects.filter(end_date__gt=timezone.now()),
            "past_programs": Program.objects.filter(end_date__lte=timezone.now()),
        }
        return data


class ProgramStageFormsetMixin:
    program_stage = None

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data()
        context["step_formset"] = ProgramRegistrationStepFormset(**self.get_formset_kwargs())
        context["step_formset_helper"] = CrispyFormsetHelper()
        return context

    def get_formset_kwargs(self):
        if self.program_stage:
            return {"instance": self.program_stage}
        return {}

    def post(self, request, *args, **kwargs):
        redirect_link = super().post(request, *args, **kwargs)
        if self.program_stage:
            step_formset = ProgramRegistrationStepFormset(request.POST, instance=self.program_stage)
            if step_formset.is_valid():
                step_formset.save()
        return redirect_link


class ProgramStageCreateView(PermissionRequiredMixin, SingleObjectMixin, ProgramStageFormsetMixin, FormView):
    permission = PermissionType.programs_edit_all
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
        # _order from order_with_respect_to
        max_index = self.object.stages.aggregate(Max('_order'))["_order__max"]
        if max_index:
            form.instance.index = max_index + 1
        form.instance.program = self.object
        self.program_stage = form.save()
        return redirect(self.get_success_url())


class ProgramStageUpdateView(PermissionRequiredMixin, ProgramStageFormsetMixin, UpdateView):
    permission = PermissionType.programs_edit_all
    model = ProgramStage
    form_class = ProgramStageForm
    context_object_name = "stage"
    template_name = "esp/program_stage_form.html"
    success_url = reverse_lazy("programs")

    def get_object(self, queryset=None):
        if not self.program_stage:
            self.program_stage = super().get_object(queryset)
        return self.program_stage


class ProgramLotteryView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.run_program_lottery
    model = Program
    template_name = "esp/program_lottery.html"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context["registrations"] = ClassRegistration.objects.filter(
            course_section__course__program_id=self.object.id
        ).values(
            "course_section__course__name", "course_section", "course_section__display_id",
        ).annotate(count=Count('id')).distinct().order_by('count')
        return context

    def post(self, request, *args, **kwargs):
        run_program_lottery(self.get_object())
        return redirect("program_lottery", pk=self.kwargs["pk"])


###########################################################


class CourseCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.courses_edit_all
    model = Course
    form_class = TeacherCourseForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["program"] = get_object_or_404(Program, pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        program_id = self.kwargs['pk']
        return reverse_lazy('courses', kwargs={'pk': program_id})


class CourseUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.courses_edit_all
    model = Course
    form_class = TeacherCourseForm
    pk_url_kwarg = "class_pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["program"] = self.object.program
        return kwargs

    def get_success_url(self):
        program_id = self.kwargs['pk']
        return reverse_lazy('courses', kwargs={'pk': self.kwargs['pk']})


class CourseListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.courses_view_all

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["program_id"] = self.kwargs['pk']
        return context

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return Course.objects.filter(program=program)
