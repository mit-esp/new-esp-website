import json

from django.db.models import OuterRef, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin

from common.constants import PermissionType
from common.views import PermissionRequiredMixin
from esp.constants import StudentRegistrationStepType
from esp.forms import UpdateStudentProfileForm
from esp.models.course_scheduling import ClassSection
from esp.models.program import (Course, PreferenceEntryCategory,
                                PreferenceEntryRound, Program)
from esp.models.program_registration import (CompletedRegistrationStep,
                                             ProgramRegistration,
                                             ProgramRegistrationStep,
                                             StudentAvailability)
from esp.serializers import ClassPreferenceSerializer

########################################################
# STUDENT REGISTRATION GENERAL VIEWS
########################################################


class ProgramRegistrationCreateView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.student_register_for_program
    model = Program
    template_name = "student/program_registration_create.html"

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        return self.object.show_to_students()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["existing_registrations"] = ProgramRegistration.objects.filter(
            program=self.object, user=self.request.user
        )
        return context

    def post(self, request, *args, **kwargs):
        registration, _created = ProgramRegistration.objects.get_or_create(program=self.object, user=self.request.user)
        return redirect("current_registration_stage", pk=registration.id)


class ProgramRegistrationStageView(PermissionRequiredMixin, DetailView):
    model = ProgramRegistration
    permission = PermissionType.student_register_for_program
    template_name = "student/program_registration_dashboard.html"

    def permission_enabled_for_view(self):
        return self.get_object().get_program_stage() is not None

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completed_steps"] = self.object.completed_steps.values_list("step_id", flat=True)
        return context


######################################################################
# STUDENT REGISTRATION STEP HANDLERS
######################################################################


class RegistrationStepBaseView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.student_register_for_program
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"
    registration_step_key = None

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        self.registration_step = get_object_or_404(
            ProgramRegistrationStep, id=self.kwargs["step_id"], step_key=self.registration_step_key
        )
        return self.registration_step.program_stage.is_active() or self.object.ignore_registration_deadlines()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset


class RegistrationStepPlaceholderView(RegistrationStepBaseView, TemplateView):
    permission = PermissionType.student_register_for_program
    template_name = "esp/registration_step_placeholder.html"

    def post(self, request, *args, **kwargs):
        return redirect(
            "complete_registration_step", registration_id=self.object.id, step_id=self.registration_step.id
        )


class VerifyStudentProfileView(RegistrationStepBaseView, FormView):
    model = ProgramRegistration
    form_class = UpdateStudentProfileForm
    template_name = "student/verify_profile.html"
    registration_step_key = StudentRegistrationStepType.verify_profile

    def get_initial(self):
        return {
            "first_name": self.object.user.first_name,
            "last_name": self.object.user.last_name,
            "email": self.object.user.email,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object.user.student_profile
        return kwargs

    def form_valid(self, form):
        self.get_object().user.update(
            first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"]
        )
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "complete_registration_step",
            kwargs={"registration_id": self.object.id, "step_id": self.registration_step.id}
        )


class SubmitWaiversView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.submit_waivers
    pass


class StudentAvailabilityView(RegistrationStepBaseView):
    registration_step_key = StudentRegistrationStepType.time_availability
    template_name = "student/time_availability.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_slots"] = self.object.program.time_slots.all()
        context["availabilities"] = self.object.availabilities.values_list("time_slot_id", flat=True)
        return context

    def post(self, request, *args, **kwargs):
        registration = self.get_object()
        for time_slot in registration.program.time_slots.all():
            if str(time_slot.id) in request.POST.keys():
                StudentAvailability.objects.update_or_create(
                    time_slot=time_slot, registration=registration
                )
            else:
                # TODO: warn if conflicts with assigned classes
                StudentAvailability.objects.filter(time_slot=time_slot, registration=registration).delete()
        return redirect("complete_registration_step", registration_id=registration.id, step_id=kwargs["step_id"])


class InitiatePreferenceEntryView(RegistrationStepBaseView):
    registration_step_key = StudentRegistrationStepType.lottery_preferences
    template_name = "student/initiate_preference_entry.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_object().program
        if not program.program_configuration:
            raise Http404("Program missing configuration")
        context["program_configuration"] = program.program_configuration
        context["step_id"] = self.registration_step.id
        return context


class ConfirmRegistrationSubmissionView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.submit_registration


class ViewAssignedCoursesView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.view_assigned_courses


class EditAssignedCoursesView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.edit_assigned_courses


class PayProgramFeesView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.pay_program_fees


class CompleteSurveysView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.complete_surveys


#####################################################################
# REGISTRATION STEP ADDITIONAL VIEWS
#####################################################################


class PreferenceEntryRoundView(PermissionRequiredMixin, DetailView):
    """View that allows a student to complete one round of preference entry"""
    model = PreferenceEntryRound
    context_object_name = "round"
    slug_url_kwarg = "index"
    slug_field = "_order"
    template_name = "student/preference_entry_round.html"

    def permission_enabled_for_view(self):
        registration_filters = {"id": self.kwargs["registration_id"]}
        if not self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            registration_filters["user_id"] = self.request.user.id
        self.registration = get_object_or_404(ProgramRegistration, **registration_filters)
        registration_step = get_object_or_404(
            ProgramRegistrationStep, id=self.kwargs["step_id"], step_key=StudentRegistrationStepType.lottery_preferences
        )
        return registration_step.program_stage.is_active() or self.registration.ignore_registration_deadlines()

    def get_queryset(self):
        # Called by self.get_object(), which is called in the super .get() and must be manually called in .post()
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
        if self.object.get_next_in_order():
            return redirect(
                "preference_entry_round",
                registration_id=self.registration.id, index=self.object.get_next_in_order()._order,
                step_id=self.kwargs["step_id"]
            )
        else:
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


class RegistrationStepCompleteView(RegistrationStepBaseView):
    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs.get("step_id"))
        CompletedRegistrationStep.objects.update_or_create(
            registration=registration, step=step, defaults={"completed_on": timezone.now()}
        )
        return redirect("current_registration_stage", pk=registration.id)
