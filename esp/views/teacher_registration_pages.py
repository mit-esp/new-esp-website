from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, TemplateView
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin

from common.constants import PermissionType
from common.views import PermissionRequiredMixin
from esp.constants import TeacherRegistrationStepType
from esp.forms import TeacherCourseForm, UpdateTeacherProfileForm
from esp.models.program import Program, TeacherProgramRegistrationStep
from esp.models.program_registration import (CompletedTeacherRegistrationStep,
                                             TeacherAvailability,
                                             TeacherRegistration)


class TeacherProgramRegistrationCreateView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.teacher_register_for_program
    model = Program
    template_name = "teacher/program_registration_create.html"

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        return self.object.show_to_teachers()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["existing_registrations"] = TeacherRegistration.objects.filter(
            program=self.object, user=self.request.user
        )
        return context

    def post(self, request, *args, **kwargs):
        registration, _created = TeacherRegistration.objects.get_or_create(program=self.object, user=self.request.user)
        return redirect("teacher_program_dashboard", pk=registration.id)


class TeacherProgramDashboardView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.teacher_register_for_program
    model = TeacherRegistration
    context_object_name = "registration"
    template_name = "teacher/program_registration_dashboard.html"

    def permission_enabled_for_view(self):
        registration = self.get_object()
        return registration.program.show_to_teachers() or registration.ignore_registration_deadlines()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.teacher_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completed_steps"] = self.object.completed_steps.values_list("step_id", flat=True)
        return context


class TeacherRegistrationStepRouterView(PermissionRequiredMixin, View):
    """Routes to the correct registration step view based on the step key"""
    permission = PermissionType.teacher_register_for_program

    def dispatch(self, request, *args, **kwargs):
        step = get_object_or_404(TeacherProgramRegistrationStep, id=kwargs["step_id"])
        view = self.route(step.step_key)
        return view(request, *args, **kwargs)

    def route(self, step_key):
        step_key_to_view = {
            TeacherRegistrationStepType.verify_profile: VerifyTeacherProfileView,
            TeacherRegistrationStepType.time_availability: TeacherAvailabilityView,

        }
        return step_key_to_view.get(step_key, TeacherRegistrationStepPlaceholderView).as_view()


class TeacherRegistrationStepBaseView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.teacher_register_for_program
    model = TeacherRegistration
    pk_url_kwarg = "registration_id"
    context_object_name = "registration"

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        self.registration_step = get_object_or_404(
            TeacherProgramRegistrationStep, id=self.kwargs["step_id"]
        )
        return self.object.has_access_to_step(self.registration_step)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.teacher_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_success_url(self):
        """Also marks step completed!"""
        CompletedTeacherRegistrationStep.objects.update_or_create(
            registration=self.object, step=self.registration_step, defaults={"completed_on": timezone.now()}
        )
        next_step = self.registration_step.get_next_in_order()
        if next_step and self.object.has_access_to_step(next_step):
            return reverse(
                "teacher_registration_step", kwargs={"registration_id": self.object.id, "step_id": next_step.id}
            )
        return reverse("teacher_program_dashboard", kwargs={"pk": self.object.id})


class TeacherRegistrationStepPlaceholderView(TeacherRegistrationStepBaseView):
    """Placeholder for registration steps while development is ongoing"""
    template_name = "esp/registration_step_placeholder.html"

    def post(self, request, *args, **kwargs):
        CompletedTeacherRegistrationStep.objects.update_or_create(
            registration=self.object, step=self.registration_step, defaults={"completed_on": timezone.now()}
        )
        return redirect("teacher_program_dashboard", pk=self.object.id)


class VerifyTeacherProfileView(TeacherRegistrationStepBaseView, FormView):
    form_class = UpdateTeacherProfileForm
    template_name = "teacher/verify_profile.html"

    def get_initial(self):
        return {
            "first_name": self.object.user.first_name,
            "last_name": self.object.user.last_name,
            "email": self.object.user.email,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object.user.teacher_profile
        return kwargs

    def form_valid(self, form):
        self.get_object().user.update(
            first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"]
        )
        form.save()
        return super().form_valid(form)


class TeacherAvailabilityView(TeacherRegistrationStepBaseView):
    template_name = "teacher/time_availability.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_slots"] = self.object.program.time_slots.all()
        context["availabilities"] = self.object.availabilities.values_list("time_slot_id", flat=True)
        return context

    def post(self, request, *args, **kwargs):
        for time_slot in self.object.program.time_slots.all():
            if str(time_slot.id) in request.POST.keys():
                TeacherAvailability.objects.update_or_create(
                    time_slot=time_slot, registration=self.object
                )
            else:
                TeacherAvailability.objects.filter(time_slot=time_slot, registration=self.object).delete()
        return redirect(self.get_success_url())


class SubmitCoursesView(TeacherRegistrationStepBaseView, FormView):
    form_class = TeacherCourseForm
    template_name = "teacher/submit_course_form.html"
