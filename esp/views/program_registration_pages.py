import json

from django.db.models import OuterRef, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin

from common.constants import PermissionType
from common.views import PermissionRequiredMixin
from esp.forms import UpdateStudentProfileForm
from esp.models.program import (ClassSection, Course, PreferenceEntryCategory,
                                PreferenceEntryRound, Program)
from esp.models.program_registration import (CompletedRegistrationStep,
                                             ProgramRegistration,
                                             ProgramRegistrationStep)
from esp.serializers import ClassPreferenceSerializer


class ProgramRegistrationCreateView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.register_for_program
    model = Program

    def permission_enabled_for_view(self):
        program = self.get_object()
        # Assumes first program stage is always initial registration
        return program.stages.first().is_active()

    def get(self, request, *args, **kwargs):
        program = self.get_object()
        registration, _created = ProgramRegistration.objects.get_or_create(program=program, user=self.request.user)
        return redirect("current_registration_stage", pk=registration.id)


class ProgramRegistrationStageView(PermissionRequiredMixin, DetailView):
    model = ProgramRegistration
    permission = PermissionType.register_for_program
    template_name = "student/program_registration_stage_dashboard.html"

    def permission_enabled_for_view(self):
        return self.get_object().get_current_stage() is not None

    def get_queryset(self):
        return ProgramRegistration.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completed_steps"] = self.object.completed_steps.values_list("step_id", flat=True)
        return context


class RegistrationStepBaseView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.register_for_program
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"

    def permission_enabled_for_view(self):
        registration_step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs["step_id"])
        return registration_step.program_stage.is_active()

    def get_queryset(self):
        return ProgramRegistration.objects.filter(user_id=self.request.user.id)


class RegistrationStepPlaceholderView(RegistrationStepBaseView, TemplateView):
    permission = PermissionType.register_for_program
    template_name = "esp/registration_step_placeholder.html"

    def post(self, request, *args, **kwargs):
        return redirect(
            "complete_registration_step", registration_id=self.kwargs["registration_id"], step_id=self.kwargs["step_id"]
        )


class VerifyStudentProfileView(RegistrationStepBaseView, FormView):
    model = ProgramRegistration
    form_class = UpdateStudentProfileForm
    template_name = "student/verify_profile.html"

    def get_form_kwargs(self):
        return {
            "instance": self.get_object().user.student_profile,
        }

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class InitiatePreferenceEntryView(RegistrationStepBaseView):
    permission = PermissionType.enter_program_lottery
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"
    template_name = "student/initiate_preference_entry.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_object().program
        if not program.program_configuration:
            raise Http404("Program missing preference entry configuration")
        context["program_configuration"] = program.program_configuration
        context["step_id"] = self.kwargs["step_id"]
        return context


class PreferenceEntryRoundView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.enter_program_lottery
    model = PreferenceEntryRound
    context_object_name = "round"
    slug_url_kwarg = "index"
    slug_field = "_order"
    template_name = "student/preference_entry_round.html"

    def permission_enabled_for_view(self):
        registration_step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs["step_id"])
        return registration_step.program_stage.is_active()

    def get_queryset(self):
        # Called by self.get_object(), which is called in the super .get() and must be manually called in .post()
        self.registration = get_object_or_404(
            ProgramRegistration, id=self.kwargs["registration_id"], user_id=self.request.user.id
        )
        return PreferenceEntryRound.objects.filter(
            program_configuration_id=self.registration.program.program_configuration_id,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration"] = self.registration
        class_sections = self.get_class_sections()
        if self.object.group_sections_by_course:
            context["courses"] = self.get_courses(class_sections)
        else:
            context["time_slots"] = {
                str(slot): class_sections.filter(time_slot_id=slot.id)
                for slot in self.registration.program.time_slots.all()
            }
        context["back_url"] = self.get_back_url()
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

    def get_back_url(self):
        if self.kwargs["index"] > 0:
            return reverse_lazy(
                "preference_entry_round",
                kwargs={
                    "registration_id": self.registration.id, "index": self.object.get_previous_in_order()._order,
                    "step_id": self.kwargs["step_id"]
                }
            )

    def get_class_sections(self):
        class_sections = ClassSection.objects.filter(course__program_id=self.registration.program_id)
        if self.object.applied_category_filter:
            previous_round = self.object.get_previous_in_order()
            if previous_round:
                try:
                    category = previous_round.categories.filter(tag=self.object.applied_category_filter).get()
                except PreferenceEntryCategory.DoesNotExist:
                    raise Http404("Misconfigured preference entry round")
                filtered_preferences = self.registration.preferences.filter(category=category, is_deleted=False)
                class_sections = class_sections.filter(
                    id__in=filtered_preferences.values("class_section_id").distinct()
                )
        class_sections = class_sections.annotate(
            user_preference=Subquery(
                self.registration.preferences.filter(
                    class_section_id=OuterRef('id'), category__preference_entry_round=self.object, is_deleted=False
                ).values("category_id")[:1]
            )
        )
        return class_sections

    def get_courses(self, class_sections):
        return Course.objects.filter(id__in=class_sections.values("course_id").distinct()).annotate(
            user_preference=Subquery(self.registration.preferences.filter(
                class_section__course_id=OuterRef('id'), category__preference_entry_round=self.object,
                is_deleted=False
            ).values("category_id")[:1])
        )


class RegistrationStepCompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.register_for_program
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"

    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs.get("step_id"))
        CompletedRegistrationStep.objects.update_or_create(
            registration=registration, step=step, defaults={"completed_on": timezone.now()}
        )
        return redirect("current_registration_stage", pk=registration.id)
