from datetime import datetime

from django.contrib import messages
from django.db.models import Count, Max, F, Value
from django.db.models.functions import Concat
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.template import Template, Context
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (CreateView, FormView, ListView, TemplateView,
                                  UpdateView)
from django.views.generic.detail import SingleObjectMixin
from multiform_views.edit import FormsView

from common.constants import PermissionType, UserType
from common.forms import CrispyFormsetHelper
from common.models import User
from common.views import PermissionRequiredMixin
from esp.constants import StudentRegistrationStepType
from config.settings import DEFAULT_FROM_EMAIL
from esp.forms import (ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, TeacherCourseForm, QuerySendEmailForm,
                       StudentSendEmailForm, TeacherSendEmailForm)
from esp.lottery import run_program_lottery
from esp.models.course_scheduling_models import ClassroomTimeSlot
from esp.models.program_models import Course, Program, ProgramStage, TimeSlot
######################################
# ADMIN DASHBOARD
######################################
from esp.models.program_registration_models import ClassRegistration, ProgramRegistration, \
    TeacherRegistration
from esp.serializers import UserSerializer


class AdminDashboardView(TemplateView):
    permission = PermissionType.admin_dashboard_view
    template_name = 'esp/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        ts = timezone.now()
        context["users_count"] = User.objects.count()
        context["students_count"] = User.objects.filter(user_type=UserType.student).count()
        context["teachers_count"] = User.objects.filter(user_type=UserType.teacher).count()
        context["admins_count"] = User.objects.filter(user_type=UserType.admin,
                                                      is_active=True).count()
        context["upcoming_program"] = Program.objects.filter(start_date__gte=ts).latest(
            'start_date', 'end_date')
        context["active_programs"] = Program.objects.filter(start_date__lte=ts,
                                                            end_date__gte=ts).order_by(
            '-start_date')
        return context


class AdminManageStudentsView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.admin_dashboard_actions
    template_name = 'esp/manage_students.html'
    model = Program

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["StudentRegistrationStepType"] = StudentRegistrationStepType
        program = self.get_object()
        context["program_id"] = program.id
        students = User.objects.filter(user_type=UserType.student,
                                       registrations__program=program).select_related(
            'student_profile')
        context['students'] = UserSerializer(students.annotate(
            search_string=Concat(F("first_name"), Value(' '), F("last_name"), Value(', ('),
                                 F("username"), Value(')'), )), many=True).data
        student_id = self.kwargs.get('student_id')
        context['student_id'] = student_id
        if context['student_id']:
            context['student_first_name'] = User.objects.get(id=student_id).first_name
            context['student_last_name'] = User.objects.get(id=student_id).last_name
            try:
                program_registration = get_object_or_404(ProgramRegistration, program=program,
                                                         user__id=student_id)
            except Http404:
                messages.ERROR(
                    f"Program Registration for program {self.kwargs['pk']} and student {student_id} does not exist")
                redirect('admin_dashboard')
            context['program_registration'] = program_registration
            context["program_stage_steps"] = program_registration.get_program_stage().steps.all()
        return context


class StudentCheckinView(PermissionRequiredMixin, View):
    permission = PermissionType.admin_dashboard_actions

    def post(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        program_id = self.kwargs.get('pk')
        program_registration = get_object_or_404(ProgramRegistration, program_id=program_id,
                                                 user_id=student_id)
        student = get_object_or_404(User, id=student_id)
        if program_registration.checked_in is False:
            program_registration.update(checked_in=True)
            messages.success(request, f"Checked in {student.first_name} {student.last_name}")
        else:
            messages.info(request,
                          f"{student.first_name} {student.last_name} is already checked in")

        return redirect('manage_students_specific', pk=program_id, student_id=student_id)


class AdminManageTeachersView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.admin_dashboard_actions
    template_name = 'esp/manage_teachers.html'
    model = Program

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        program = self.get_object()
        context["program_id"] = program.id
        timeslots = TimeSlot.objects.filter(program=program).order_by('start_datetime')
        context["timeslot_list"] = self.get_time_list(timeslots)
        return context

    def get_time_list(self, timeslots: datetime):
        """organizes the datetimes into a list of lists with each sublist containing datetimes
            from a single day"""
        time_list = [[timeslots[0]]]
        for time in timeslots[1:]:
            if time.start_datetime.date() == time_list[-1][-1].start_datetime.date():
                time_list[-1].append(time)
            else:
                time_list.append([time])
        return time_list


class AdminCheckinTeachersView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.admin_dashboard_actions
    template_name = 'esp/check_in_teachers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["program_id"] = self.kwargs["pk"]
        timeslot_id = self.kwargs["timeslot_id"]
        context["timeslot_id"] = timeslot_id
        if self.kwargs["unit"] == 'day':
            day = TimeSlot.objects.get(id=timeslot_id).start_datetime.day
            classroom_timeslots = ClassroomTimeSlot.objects.filter(time_slot__start_datetime__day=day)
        elif self.kwargs["unit"] == 'slot':
            classroom_timeslots = ClassroomTimeSlot.objects.filter(time_slot_id=timeslot_id)
        else:
            raise Http404
        context["courses_list"] = self.get_courses_list(classroom_timeslots)
        return context

    def get_courses_list(self, classroom_timeslots):
        courses_list = []
        for classroom_timeslot in classroom_timeslots:
            course_dict = {'course': classroom_timeslot.course_section.course,
                           'classroom': classroom_timeslot.classroom.name, 'teachers': [], }
            for teacher in classroom_timeslot.course_section.course.teacher_registrations.all():
                checked_in = teacher.check_in_time and teacher.check_in_time.date() == timezone.now().date()
                course_dict['teachers'].append({'teacher': teacher, 'checked_in': checked_in})
            courses_list.append(course_dict)
        return courses_list


class TeacherCheckinView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.admin_dashboard_actions
    model = TeacherRegistration
    pk_url_kwarg = 'teacher_id'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
        teacher_registration = self.get_object()
        timeslot_id = self.kwargs.get('timeslot_id')
        if teacher_registration.check_in_time and teacher_registration.check_in_time.date() == timezone.now().date():
            messages.info(request,
                          f"{teacher_registration.user.first_name} {teacher_registration.user.last_name} already checked in today")
        else:
            teacher_registration.update(check_in_time=timezone.now())
            messages.success(request,
                             f"Checked in {teacher_registration.user.first_name} {teacher_registration.user.last_name}")

        return redirect('check_in_teachers', pk=teacher_registration.program.id,
                        timeslot_id=timeslot_id)


class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.admin_dashboard_actions
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


class SendEmailsView(PermissionRequiredMixin, FormsView):
    permission = PermissionType.send_email
    template_name = "esp/send_email.html"
    success_url = reverse_lazy('send_email')
    mailing_list = None
    form_classes = {
        'query_form': QuerySendEmailForm,
        'teacher_form': TeacherSendEmailForm,
        'student_form': StudentSendEmailForm,
    }

    def query_form_valid(self, form):
        users = form.cleaned_data['users']
        self._send_emails(users, form)
        return HttpResponseRedirect(self.success_url)

    def teacher_form_valid(self, form):
        # print(form.cleaned_data)
        teachers = User.objects.filter(user_type=UserType.teacher)
        if form.cleaned_data['program']:
            # print(form.cleaned_data['program'])
            teachers = teachers.filter(teacher_registrations__program=form.cleaned_data['program'])
        if form.cleaned_data['submit_one_class']:
            teachers = teachers.annotate(
                num_courses=Count('teacher_registrations__courses')).filter(num_courses__gte=1)
        if form.cleaned_data['difficulty']:
            teachers = teachers.filter(
                teacher_registrations__courses__course__difficulty=form.cleaned_data['difficulty'])
        if form.cleaned_data['registration_step']:
            teachers = teachers.filter(
                teacher_registrations__completed_steps__step__step_key=form.cleaned_data[
                    'registration_step'])
        self._send_emails(teachers, form)
        return HttpResponseRedirect(self.success_url)

    def student_form_valid(self, form):
        students = User.objects.filter(user_type=UserType.student)
        if form.cleaned_data['program']:
            students = students.filter(registrations__program=form.cleaned_data['program'])
        if form.cleaned_data['registration_step']:
            students = students.filter(
                registrations__completed_steps__step__step_key=form.cleaned_data[
                    'registration_step'])
        only_guardians = form.cleaned_data['only_guardians']
        self._send_emails(students, form, only_guardians)
        return HttpResponseRedirect(self.success_url)

    def _send_emails(self, to_users, form, only_guardians=False, emergency_contacts=False):
        subject = form.cleaned_data['subject']
        from_email = DEFAULT_FROM_EMAIL
        template = Template(form.cleaned_data['body'])

        for to_user in to_users:
            # This dict contains the available merge fields that you can use in sending emails
            # add to this dict to add to the available fields you can use in the email body ex.
            # to insert a user's first name into an email, type '{{ first_name }}'. You may
            # access any field or related object of a user with dot notation ex. {{
            # user.teacher_profile.graduation_year }}. If a merge field is used in the body that
            # is not present in the context_dict then that field will be replaced by the empty
            # string
            # NOTE: merge fields currently ony available for use in the email body. To use in the
            # subject line or elsewhere, follow the same pattern used for rendering the template
            # in the body
            context_dict = {
                'user': to_user,
                'first_name': to_user.first_name,
                'last_name': to_user.last_name,
                'username': to_user.username,
                'email': to_user.email,
            }
            if only_guardians:
                context_dict['first_name'] = to_user.student_profile.guardian_first_name
                context_dict['last_name'] = to_user.student_profile.guardian_last_name
                context_dict['email'] = to_user.student_profile.guardian_email or to_user.email
                body = template.render(Context(context_dict))
                to_emails = [to_user.student_profile.guardian_email]
            else:
                body = template.render(Context(context_dict))
                to_emails = [to_user.email]

            send_mail(
                subject,
                body,
                from_email,
                to_emails,
                fail_silently=False,
            )

        email_count = to_users.count()
        messages.success(self.request,
                         f'An email was sent to {email_count} email address{"" if email_count == 1 else "es"}')


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

    def form_valid(self, form):
        self.program = get_object_or_404(Program, pk=self.kwargs['pk'])
        form.instance.program = self.program
        return super().form_valid(form)


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
