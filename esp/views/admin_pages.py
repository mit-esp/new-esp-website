import smtplib
from email.message import EmailMessage

from django.contrib import messages
from django.core.exceptions import FieldError
from django.core.mail import send_mail
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, FormView, ListView, TemplateView,
                                  UpdateView)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from common.constants import PermissionType, UserType
from common.forms import CrispyFormsetHelper
from common.models import User
from common.views import PermissionRequiredMixin
from config.settings import DEFAULT_FROM_EMAIL
from esp.forms import (ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, TeacherCourseForm, QuerySendEmailForm,
                       StudentSendEmailForm, TeacherSendEmailForm)
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
        context["users_count"] = User.objects.count()
        context["students_count"] = User.objects.filter(user_type=UserType.student).count()
        context["teachers_count"] = User.objects.filter(user_type=UserType.teacher).count()
        context["admins_count"] = User.objects.filter(user_type=UserType.admin,
                                                      is_active=True).count()
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
    model = Program


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


class ProgramStageCreateView(PermissionRequiredMixin, SingleObjectMixin, ProgramStageFormsetMixin,
                             FormView):
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
        max_index = self.object.stages.aggregate(Max('index'))["index__max"]
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


class SendEmailsView(PermissionRequiredMixin, FormMixin, TemplateView):
    permission = PermissionType.send_email
    template_name = "esp/send_email.html"
    success_url = reverse_lazy('admin_dashboard')
    mailing_list = None
    forms = {
        'query_form': QuerySendEmailForm,
        'student_form': StudentSendEmailForm,
        'teacher_form': TeacherSendEmailForm,
    }

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.forms)

    def get_form(self, post_request):
        """Return an instance of the form to be used in this view."""
        form_class = None
        for name, _ in self.forms.items():
            if name in post_request:
                form_class = self.forms[name]
        if form_class is None:
            raise Exception
        return form_class(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Ensures that the inputted query is valid. The form takes in a list of comma separated
        Django clauses on the User model that will be ANDed together to form one query on the
        User model. Any spaces will be removed before parsing. If any part of any of the clauses
        is not formatted correctly, the form will be invalid.
        """
        print(type(form))
        print(form.cleaned_data)
        to_emails = []
        if form is QuerySendEmailForm:
            try:
                query = form.cleaned_data['query'].replace(' ', '')
                kwargs = {}
                for arg in query.split(','):
                    x, y = arg.split('=')
                    kwargs[x] = y
                to_emails = User.objects.filter(**kwargs).values_list('email', flat=True)
            except (FieldError, ValueError) as e:
                form.add_error('query', 'Query is not a valid format')
                return super().form_invalid(form)
        elif form is TeacherSendEmailForm:
            teachers = User.objects.filter(user_type=UserType.teacher)
            if form.cleaned_data['submit_one_class']:
                 pass
            if form.cleaned_data['difficulty']:
                 pass
            if form.cleaned_data['registration_step']:
                 pass
            to_emails.append(teachers.value_list('email', flat=True))
        elif form is StudentSendEmailForm:
            students = User.objects.filter(user_type=UserType.teacher)
            if form.cleaned_data['registration_step']:
                pass
            to_emails.append(students.value_list('email', flat=True))
            if form.cleaned_data['guardians']:
                to_emails.append(students.value_list('guardian_email', flat=True))
            if form.cleaned_data['emergency_contact']:
                to_emails.append(students.value_list('emergency_contact_email', flat=True))
        else:
            raise Exception

        # if mailing list is empty, return to the form
        if not to_emails:
            return super().form_invalid(form)

        # send emails to mailing list
        subject = form.cleaned_data['subject']
        from_email = DEFAULT_FROM_EMAIL
        body = form.cleaned_data['body']
        send_mail(
            subject,
            body,
            from_email,
            to_emails,
            fail_silently=False,
        )
        return super().form_valid(form)


###########################################################


class CourseCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.courses_edit_all
    model = Course
    form_class = TeacherCourseForm
    success_url = reverse_lazy('programs')


class CourseUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.courses_edit_all
    model = Course
    form_class = TeacherCourseForm
    success_url = reverse_lazy('programs')


class CourseListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.courses_view_all
    model = Course
