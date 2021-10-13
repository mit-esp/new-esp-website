import json

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, FormView, UpdateView

from common.constants import UserType
from common.forms import CrispyFormsetHelper
from esp.forms import (CourseForm, ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, RegisterUserForm, StudentProfileForm,
                       UpdateStudentProfileForm)
from esp.models import (ClassSection, CompletedRegistrationStep, Course,
                        PreferenceEntryCategory, PreferenceEntryRound, Program,
                        ProgramRegistration, ProgramRegistrationStep,
                        ProgramStage, StudentProfile)
from esp.serializers import ClassPreferenceSerializer


class RegisterAccountView(CreateView):
    template_name = "registration.html"
    form_class = RegisterUserForm

    def get_success_url(self):
        profile_form_url_mapping = {
            UserType.student: "create_student_profile",
        }
        return reverse(profile_form_url_mapping.get(self.object.user_type, self.object.get_dashboard_url()))

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)


class StudentProfileCreateView(CreateView):
    model = StudentProfile
    form_class = StudentProfileForm
    success_url = reverse_lazy("student_dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StudentProfileUpdateView(UpdateView):
    model = StudentProfile
    form_class = UpdateStudentProfileForm
    success_url = reverse_lazy("student_dashboard")

    def get_initial(self):
        return {
            "first_name": self.object.user.first_name,
            "last_name": self.object.user.last_name,
            "email": self.object.user.email,
        }

    def form_valid(self, form):
        self.object.user.update(
            first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"]
        )
        return super().form_valid(form)

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


class VolunteerDashboardView(BaseDashboardView):
    template_name = 'dashboards/volunteer_dashboard.html'

#######################################################


class ProgramRegistrationCreateView(SingleObjectMixin, View):
    model = Program

    def get(self, request, *args, **kwargs):
        program = self.get_object()
        registration, _created = ProgramRegistration.objects.get_or_create(
            program=program, user=self.request.user, defaults={"program_stage": program.stages.first()}
        )
        return redirect("current_registration_stage", pk=registration.id)


class ProgramRegistrationStageView(DetailView):
    model = ProgramRegistration

    def get_queryset(self):
        return ProgramRegistration.objects.filter(user_id=self.request.user.id)


class InitiatePreferenceEntryView(DetailView):
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"
    template_name = "esp/initiate_preference_entry.html"

    def get_queryset(self):
        return ProgramRegistration.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.program.preference_entry_configuration:
            raise Http404("Program missing preference entry configuration")
        context["preference_entry_configuration"] = self.object.program.preference_entry_configuration
        context["step_id"] = self.kwargs["step_id"]
        return context


class PreferenceEntryRoundView(DetailView):
    model = PreferenceEntryRound
    context_object_name = "round"
    slug_url_kwarg = "index"
    slug_field = "_order"
    template_name = "esp/preference_entry_round.html"

    def get_queryset(self):
        # Called by self.get_object(), which must be manually called in .post()
        self.registration = get_object_or_404(
            ProgramRegistration, id=self.kwargs["registration_id"], user_id=self.request.user.id
        )
        return PreferenceEntryRound.objects.filter(
            preference_entry_configuration_id=self.registration.program.preference_entry_configuration_id,
        )

    def back_url(self):
        if self.kwargs["index"] > 0:
            return reverse_lazy(
                "preference_entry_round",
                kwargs={
                    "registration_id": self.registration.id, "index": self.object.get_previous_in_order()._order,
                    "step_id": self.kwargs["step_id"]
                }
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration"] = self.registration
        class_sections = ClassSection.objects.filter(course__program_id=self.registration.program_id)
        if self.object.applied_category_filter:
            previous_round = self.object.get_previous_in_order()
            if previous_round:
                try:
                    category = previous_round.categories.filter(tag=self.object.applied_category_filter).get()
                except PreferenceEntryCategory.DoesNotExist:
                    raise Http404("Misconfigured preference entry round")
                filtered_preferences = self.registration.preferences.filter(category=category)
                if category.has_integer_value and self.object.applied_category_min_value:
                    filtered_preferences = filtered_preferences.filter(
                        value__gte=self.object.applied_category_min_value
                    )
                if category.has_integer_value and self.object.applied_category_max_value:
                    filtered_preferences = filtered_preferences.filter(
                        value__lte=self.object.applied_category_max_value
                    )
                class_sections = class_sections.filter(
                    id__in=filtered_preferences.values("class_section_id").distinct()
                )
        if self.object.group_sections_by_course:
            context["courses"] = Course.objects.filter(id__in=class_sections.values("course_id").distinct())
        else:
            context["time_slots"] = {
                str(slot): class_sections.filter(time_slot_id=slot.id)
                for slot in self.registration.program.time_slots.all()
            }
        context["back_url"] = self.back_url()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = json.loads(request.POST.get("data"))
        serializer = ClassPreferenceSerializer(data=data, many=True, context={
            "group_sections_by_course": self.object.group_sections_by_course,
            "registration": self.registration,
            "preference_entry_round_id": self.object.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            return redirect(
                "preference_entry_round",
                registration_id=self.registration.id, index=self.object.get_next_in_order()._order,
                step_id=self.kwargs["step_id"]
            )
        except PreferenceEntryRound.DoesNotExist:
            return redirect(
                "complete_registration_step",
                registration_id=self.registration.id, step_id=self.kwargs["step_id"]
            )


class RegistrationStepCompleteView(SingleObjectMixin, View):
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"

    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs.get("step_id"))
        CompletedRegistrationStep.objects.update_or_create(registration=registration, step=step)
        return redirect("current_registration_stage", pk=registration.id)


class RegistrationStepPlaceholderView(TemplateView):
    template_name = "esp/registration_step_placeholder.html"

    def post(self, request, *args, **kwargs):
        return redirect(
            "complete_registration_step", registration_id=self.kwargs["registration_id"], step_id=self.kwargs["step_id"]
        )
