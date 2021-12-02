import json

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Exists, F, Min, OuterRef, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin

from common.constants import PermissionType
from common.views import PermissionRequiredMixin
from esp.constants import StudentRegistrationStepType
from esp.forms import UpdateStudentProfileForm
from esp.models.course_scheduling import CourseSection
from esp.models.program import (Course, PreferenceEntryCategory,
                                PreferenceEntryRound, Program, TimeSlot)
from esp.models.program_registration import (ClassRegistration,
                                             CompletedRegistrationStep,
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
        self.object = self.get_object()
        self.program_stage = self.object.get_program_stage()
        return self.program_stage is not None

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["program"] = self.object.program
        context["program_stage"] = self.program_stage
        context["program_stage_steps"] = self.program_stage.steps.all()
        context["completed_steps"] = self.object.completed_steps.values_list("step_id", flat=True)
        course_registrations = list(
            self.object.class_registrations.filter(confirmed_on__isnull=False)
            .annotate(start_time=Min("course_section__time_slots__time_slot__start_datetime"))
            .order_by("start_time")
            .select_related("course_section", "course_section__course", "course_section__course__program")
            .prefetch_related(
                "course_section__time_slots__time_slot", "course_section__course__teachers__teacher_registration__user"
            )
        )
        context["course_registrations"] = course_registrations
        return context


######################################################################
# STUDENT REGISTRATION STEP HANDLERS
######################################################################


class RegistrationStepBaseView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
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


class RegistrationStepPlaceholderView(RegistrationStepBaseView):
    permission = PermissionType.student_register_for_program
    template_name = "esp/registration_step_placeholder.html"

    def post(self, request, *args, **kwargs):
        return redirect(
            "complete_registration_step", registration_id=self.object.id, step_id=self.registration_step.id
        )


class VerifyStudentProfileView(RegistrationStepBaseView, FormView):
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


class ConfirmRegistrationSubmissionView(RegistrationStepBaseView):
    registration_step_key = StudentRegistrationStepType.submit_registration
    template_name = "student/confirm_courses.html"

    def post(self, *args, **kwargs):
        # TODO: Send confirmation email
        return redirect("complete_registration_step", registration_id=self.object.id, step_id=self.registration_step.id)


class ConfirmAssignedCoursesView(RegistrationStepBaseView):
    registration_step_key = StudentRegistrationStepType.confirm_assigned_courses
    template_name = "student/confirm_courses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_registrations"] = (
            self.object.class_registrations.select_related("course_section", "course_section__course")
            .prefetch_related("course_section__course__teachers__teacher_registration__user")
        )
        return context

    def post(self, *args, **kwargs):
        self.object.class_registrations.all().update(confirmed_on=timezone.now())
        # TODO: Send confirmation email
        return redirect("complete_registration_step", registration_id=self.object.id, step_id=self.registration_step.id)


class PayProgramFeesView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.pay_program_fees


class CompleteSurveysView(RegistrationStepPlaceholderView):
    registration_step_key = StudentRegistrationStepType.complete_surveys


#####################################################################
# REGISTRATION STEP ADDITIONAL VIEWS
#####################################################################


class PreferenceEntryRoundView(PermissionRequiredMixin, DetailView):
    """View that allows a student to complete one round of preference entry"""
    permission = PermissionType.student_register_for_program
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
        course_sections = self.get_course_sections()
        if self.object.group_sections_by_course:
            context["courses"] = self.get_courses(course_sections)
        else:
            context["time_slots"] = {
                str(slot): course_sections.filter(time_slots__time_slot_id=slot.id)
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

    def get_course_sections(self):
        course_sections = CourseSection.objects.filter(course__program_id=self.registration.program_id)
        if self.object.applied_category_filter:
            previous_round = self.object.get_previous_in_order()
            if previous_round:
                try:
                    category = previous_round.categories.filter(tag=self.object.applied_category_filter).get()
                except PreferenceEntryCategory.DoesNotExist:
                    raise Http404("Misconfigured preference entry round")
                filtered_preferences = self.registration.preferences.filter(category=category, is_deleted=False)
                course_sections = course_sections.filter(
                    id__in=filtered_preferences.values("course_section_id").distinct()
                )
        course_sections = course_sections.annotate(
            user_preference=Subquery(
                self.registration.preferences.filter(
                    course_section_id=OuterRef('id'), category__preference_entry_round=self.object, is_deleted=False
                ).values("category_id")[:1]
            )
        )
        return course_sections

    def get_courses(self, course_sections):
        return Course.objects.filter(id__in=course_sections.values("course_id").distinct()).annotate(
            user_preference=Subquery(self.registration.preferences.filter(
                course_section__course_id=OuterRef('id'), category__preference_entry_round=self.object,
                is_deleted=False
            ).values("category_id")[:1])
        )


class EditAssignedCoursesView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.student_register_for_program
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"
    template_name = "student/swap_courses.html"

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        return self.object.class_registrations.exists()

    def get_queryset(self):
        if self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            return super().get_queryset()
        return super().get_queryset().filter(program_registration__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        swap_id = self.request.GET.get('swap')
        if swap_id:
            context["registration_to_swap"] = ClassRegistration.objects.get(id=swap_id)
        context["available_courses"] = self.get_available_courses(swap_id)
        return context

    def post(self, request, *args, **kwargs):
        course_section_id = self.request.POST.get("course_section_id")
        if not course_section_id:
            messages.error(self.request, message='Invalid submission')
        with transaction.atomic():
            ClassRegistration.objects.filter(
                program_registration__program_id=self.object.program_id).select_for_update()
            context = self.get_context_data()
            try:
                context["available_courses"].get(id=course_section_id)
                ClassRegistration.objects.create(
                    course_section_id=course_section_id, program_registration_id=self.object.id,
                    created_by_lottery=False, confirmed_on=timezone.now()
                )
                if context.get("registration_to_swap"):
                    registration = context["registration_to_swap"]
                    registration.delete()
                if self.request.GET.get('next'):
                    return redirect(self.request.GET.get('next'))
                return redirect('current_registration_stage')
            except CourseSection.DoesNotExist:
                messages.error(self.request, 'This course is no longer available')

    def get_available_courses(self, swap_id):
        student_unavailable_timeslots = (
            self.object.class_registrations.exclude(id=swap_id).values("course_section__time_slots__time_slot_id")
        )
        student_courses = self.object.class_registrations.exclude(id=swap_id).values('course_section__course_id')
        return (
            CourseSection.objects.exclude(registrations__isnull=False, registrations__id=swap_id)
            .filter(course__program_id=self.object.program_id)
            .exclude(course_id__in=student_courses).distinct()
            .annotate(num_registrations=Count("registrations"))
            .filter(num_registrations__lt=F('course__max_section_size'))
            .annotate(student_unavailable=Exists(
                TimeSlot.objects.filter(
                    id__in=student_unavailable_timeslots, classrooms__course_section_id=OuterRef('id')
                ))
            )
        )


class DeleteCourseRegistrationView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.student_register_for_program
    model = ClassRegistration

    def get_queryset(self):
        if self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            return super().get_queryset()
        return super().get_queryset().filter(program_registration__user=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            course_registration = self.get_object()
            course_registration.delete()
        except ClassRegistration.DoesNotExist:
            messages.error(request, message='Action not allowed')
        if self.request.GET.get('next'):
            return redirect(self.request.GET.get('next'))
        return redirect('current_registration_stage')


class RegistrationStepCompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.student_register_for_program
    model = ProgramRegistration
    pk_url_kwarg = "registration_id"

    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        step = get_object_or_404(ProgramRegistrationStep, id=self.kwargs.get("step_id"))
        CompletedRegistrationStep.objects.update_or_create(
            registration=registration, step=step, defaults={"completed_on": timezone.now()}
        )
        return redirect("current_registration_stage", pk=registration.id)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.student_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset
