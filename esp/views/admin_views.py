from collections import defaultdict

from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import (BooleanField, Count, ExpressionWrapper, F, Max,
                              Min, OuterRef, Prefetch, Q, Subquery, Sum, Value)
from django.db.models.functions import Concat
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, Template
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, FormView, ListView, TemplateView,
                                  UpdateView)
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from multiform_views.edit import FormsView

from common.constants import PermissionType, UserType
from common.forms import CrispyFormsetHelper
from common.models import User
from common.views import PermissionRequiredMixin
from config.settings import DEFAULT_FROM_EMAIL
from esp.constants import PaymentMethod, StudentRegistrationStepType
from esp.forms import (CommentForm, ProgramForm, ProgramRegistrationStepFormset,
                       ProgramStageForm, QuerySendEmailForm,
                       StudentSendEmailForm, TeacherCourseForm,
                       TeacherSendEmailForm)
from esp.legacy.latex import render_to_latex
from esp.lottery import LotteryDisallowedError, run_program_lottery
from esp.models.course_scheduling_models import (ClassroomTimeSlot,
                                                 CourseSection)
from esp.models.program_models import (Course, Program, ProgramStage,
                                       PurchaseableItem, TimeSlot)
from esp.models.program_registration_models import (ClassRegistration,
                                                    FinancialAidRequest,
                                                    ProgramRegistration,
                                                    PurchaseLineItem,
                                                    TeacherRegistration,
                                                    UserPayment)
from esp.serializers import CommentSerializer, UserSerializer

######################################
# ADMIN DASHBOARD
######################################


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
        context["upcoming_programs"] = Program.objects.filter(start_date__gte=ts).order_by('start_date', 'end_date')[:3]
        context["active_programs"] = (
            Program.objects.filter(start_date__lte=ts, end_date__gte=ts).order_by('-start_date')
        )
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
        students = User.objects.filter(student_profile__isnull=False,
                                       registrations__program=program).select_related(
            'student_profile')
        context['students'] = UserSerializer(students.annotate(
            search_string=Concat(F("first_name"), Value(' '), F("last_name"), Value(', ('),
                                 F("username"), Value(')'), )), many=True).data
        student_id = self.kwargs.get('student_id')
        context['student_id'] = student_id
        if context['student_id']:
            try:
                student = get_object_or_404(User, id=student_id)
                context['student'] = student
                purchased_items_query = PurchaseLineItem.objects.filter(user=student, item__id=OuterRef("id"))
                context["purchase_items"] = program.purchase_items.annotate(
                    in_cart=Count(purchased_items_query.filter(purchase_confirmed_on__isnull=True).distinct().values("id")),
                    in_cart_price=Subquery(
                        purchased_items_query.filter(purchase_confirmed_on__isnull=True)[:1].values("charge_amount")
                    ),
                    purchased=Count(
                        purchased_items_query.filter(purchase_confirmed_on__isnull=False).distinct().values("id")),
                )
                context['purchased'] = student.purchases.filter(item__program=program, purchase_confirmed_on__isnull=False).select_related(
                    'item', 'payment'
                )
                program_registration = get_object_or_404(ProgramRegistration, program=program, user__id=student_id)
                context['program_registration'] = program_registration
                context["program_stage_steps"] = program_registration.get_program_stage().steps.all()
                context["financial_aid_approved"] = (
                    program_registration.financial_aid_requests.filter(approved=True).exists()
                )
                context['comments'] = program_registration.comments.values_list('comment', 'author__username', 'created_on')

                context['comment_form'] = CommentForm(program_registration)
            except Http404:
                messages.error(
                    self.request,
                    f"Program Registration for program {self.kwargs['pk']} and student {student_id} does not exist"
                )
                redirect('admin_dashboard')
        return context

class AdminCommentView(PermissionRequiredMixin, View):
    permission = PermissionType.admin_dashboard_actions

    def post(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        program_id = self.kwargs.get('pk')
        program_registration = get_object_or_404(ProgramRegistration, program_id=program_id,
                                                 user_id=student_id)
        student = get_object_or_404(User, id=student_id)
        print(request.POST)
        data = {"author": request.user.id,
                "registration": program_registration.id,
                "comment": request.POST["comment"]}
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            messages.error(
                self.request,
                serializer.errors
            )
        return redirect('manage_students_specific', pk=program_id, student_id=student_id)


class StudentCheckinView(PermissionRequiredMixin, View):
    permission = PermissionType.admin_dashboard_actions

    def post(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        program_id = self.kwargs.get('pk')
        program_registration = get_object_or_404(ProgramRegistration, program_id=program_id,
                                                 user_id=student_id)
        student = get_object_or_404(User, id=student_id)
        if program_registration.checked_in is False:
            registration_requirements_check = program_registration.check_registration_requirements()
            if registration_requirements_check["requirements_satisfied"]:
                program_registration.update(checked_in=True)
                messages.success(request, f"Checked in {student.first_name} {student.last_name}")
            else:
                for message in registration_requirements_check["errors"]:
                    messages.error(request, message)
        else:
            messages.info(request,
                          f"{student.first_name} {student.last_name} is already checked in")

        return redirect('manage_students_specific', pk=program_id, student_id=student_id)


class StudentCashPaymentView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.admin_dashboard_actions
    model = ProgramRegistration
    pk_url_kwarg = "student_id"

    def post(self, request, *args, **kwargs):
        registration = self.get_object()
        # Parse item ids from POST data
        new_cart_item_ids = [key[5:] for key in request.POST.keys() if key.startswith('item-')]
        new_cart_items = PurchaseableItem.objects.filter(id__in=new_cart_item_ids, program=registration.program)
        purchases_to_create = []
        fin_aid = registration.financial_aid_requests.filter(approved=True).exists()
        for item in new_cart_items:
            # Assumes 100% financial aid for all eligible items
            price = 0 if item.eligible_for_financial_aid and fin_aid else item.price
            purchases_to_create.append(
                PurchaseLineItem(
                    user=registration.user, item=item, added_to_cart_on=timezone.now(), charge_amount=price
                )
            )
        PurchaseLineItem.objects.bulk_create(purchases_to_create)
        whole_cart = registration.user.purchases.filter(
            item__program=registration.program, purchase_confirmed_on__isnull=True
        )
        num_items = whole_cart.count()
        total_charge = whole_cart.aggregate(total_charge=Sum("charge_amount"))["total_charge"]
        payment = UserPayment.objects.create(
            user=registration.user,
            payment_method=PaymentMethod.cash,
            total_amount=total_charge,
            transaction_datetime=timezone.now(),
        )
        whole_cart.update(payment=payment, purchase_confirmed_on=timezone.now())
        messages.success(request, f"A total payment of ${total_charge} ({num_items} items) has been logged.")
        return redirect("manage_students_specific", pk=registration.program_id, student_id=registration.user_id)


class AdminManageTeachersView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.admin_dashboard_actions
    template_name = 'esp/manage_teachers.html'
    model = Program

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context["program_id"] = self.object.id
        course_sections = CourseSection.objects.filter(course__program=self.object)
        context["timeslot_dict"] = self.get_time_dict(course_sections)
        return context

    def get_time_dict(self, sections):
        """organizes the datetimes into a dict of lists with each key being a date and each list
            being the datetimes from that day"""
        time_dict = defaultdict(list)
        for section in sections:
            for meeting in section.get_section_times():
                timeslot = TimeSlot.objects.get(program=self.object, start_datetime=meeting[0])
                if timeslot not in time_dict[meeting[0].date()]:
                    time_dict[meeting[0].date()].append(timeslot)
        for key, value in time_dict.items():
            value.sort(key=lambda x: x.start_datetime)
        time_dict.default_factory = None
        return time_dict


class AdminCheckinTeachersView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.admin_dashboard_actions
    template_name = 'esp/check_in_teachers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        program_id = self.kwargs["pk"]
        context["program_id"] = program_id
        unit = self.kwargs["unit"]
        context["unit"] = unit
        timeslot_id = self.kwargs["timeslot_id"]
        context["timeslot_id"] = timeslot_id
        time_slot = TimeSlot.objects.get(id=timeslot_id)
        context["time_range"] = time_slot.start_datetime.time() if unit == "slot" else time_slot.start_datetime.date()
        sections = CourseSection.objects.filter(course__program_id=program_id)
        classroom_timeslots = []
        if self.kwargs["unit"] == 'day':
            day = TimeSlot.objects.get(id=timeslot_id).start_datetime.date()
            sections = sections.filter(time_slots__time_slot__start_datetime__date=day).distinct()
            for section in sections:
                course_times = section.get_section_times()
                for time in course_times:
                    if time[0].date() == day:
                        classroom_timeslots.append(ClassroomTimeSlot.objects.get(
                            course_section=section,
                            time_slot=TimeSlot.objects.get(program_id=program_id,
                                                           start_datetime=time[0],
                                                           ),
                        ))
        elif self.kwargs["unit"] == 'slot':
            sections = sections.filter(time_slots__time_slot_id=timeslot_id).distinct()
            for section in sections:
                course_times = section.get_section_times()
                for time in course_times:
                    if time[0] == time_slot.start_datetime:
                        classroom_timeslots.append(ClassroomTimeSlot.objects.get(
                            course_section=section,
                            time_slot=time_slot,
                        ))
        else:
            raise Http404
        course_list = self.get_courses_list(classroom_timeslots)
        context["courses_list"] = sorted(course_list, key=lambda x: x['classroom_info'].time_slot.start_datetime.time())
        return context

    def get_courses_list(self, classroom_timeslots):
        courses_list = []
        today = timezone.now().date()
        for classroom_timeslot in classroom_timeslots:
            course_dict = {
                'course': classroom_timeslot.course_section.course,
                'classroom_info': classroom_timeslot,
                'teachers': classroom_timeslot.course_section.course.teacher_registrations.annotate(
                    checked_in=ExpressionWrapper(
                        Q(checked_in_at__isnull=False, checked_in_at__date=today),
                        output_field=BooleanField()
                    )
                ),
            }
            courses_list.append(course_dict)
        return courses_list


class TeacherCheckinView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.admin_dashboard_actions
    model = TeacherRegistration
    pk_url_kwarg = 'teacher_id'

    def post(self, request, *args, **kwargs):
        teacher_registration = self.get_object()
        timeslot_id = self.kwargs.get('timeslot_id')
        if teacher_registration.checked_in_at and teacher_registration.checked_in_at.date() == timezone.now().date():
            messages.info(
                request,
                f"{teacher_registration.user.first_name} {teacher_registration.user.last_name} already checked in today"
            )
        else:
            reg_requirements_check = teacher_registration.check_registration_requirements()
            if reg_requirements_check["requirements_satisfied"]:
                teacher_registration.update(checked_in_at=timezone.now())
                messages.success(
                    request,
                    f"Checked in {teacher_registration.user.first_name} {teacher_registration.user.last_name}"
                )
            else:
                for message in reg_requirements_check["errors"]:
                    messages.error(request, message)
        return redirect('check_in_teachers', pk=teacher_registration.program.id,
                        timeslot_id=timeslot_id, unit=self.kwargs.get('unit'))


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
        try:
            registrations_count = run_program_lottery(self.get_object())
            if registrations_count == 0:
                messages.warning(request, "No course registrations created. Have students submitted preferences?")
            else:
                messages.success(request, f"{registrations_count} course registrations created")
        except LotteryDisallowedError as e:
            messages.error(request, str(e))
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
        teachers = User.objects.filter(user_type=UserType.teacher)
        if form.cleaned_data['program']:
            teachers = teachers.filter(teacher_registrations__program=form.cleaned_data['program'])
        if form.cleaned_data['submit_one_class']:
            teachers = teachers.annotate(
                num_courses=Count('teacher_registrations__courses')).filter(num_courses__gte=1)
        if form.cleaned_data['difficulty']:
            teachers = teachers.filter(
                teacher_registrations__courses__difficulty=form.cleaned_data['difficulty'])
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
        messages.success(
            self.request, f'An email was sent to {email_count} email address{"" if email_count == 1 else "es"}'
        )


class PrintStudentSchedulesView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission = PermissionType.admin_dashboard_view
    model = Program

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "registrations__user",
            Prefetch("registrations__class_registrations", queryset=ClassRegistration.objects.annotate(
                start_time=Min("course_section__time_slots__time_slot__start_datetime")).order_by("start_time")
            ),
            "registrations__class_registrations__course_section__time_slots",
            "registrations__class_registrations__course_section__course__program",
        )

    def get(self, request, *args, **kwargs):
        program = self.get_object()
        return render_to_latex("latex/student_schedules_all.tex", context_dict={"program": program})


class ApproveFinancialAidView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    model = Program
    permission = PermissionType.admin_dashboard_view
    template_name = "esp/approve_financial_aid.html"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context["financial_aid_requests_count"] = (
            FinancialAidRequest.objects
            .filter(program_registration__program=self.object, reviewed_on__isnull=True)
            .count()
        )
        return context

    def post(self, request, *args, **kwargs):
        program = self.get_object()
        requests = FinancialAidRequest.objects.filter(program_registration__program=program, reviewed_on__isnull=True)
        # Update all eligible items already in requesters' carts
        PurchaseLineItem.objects.filter(
            purchase_confirmed_on__isnull=True,
            payment__isnull=True,
            user__in=requests.values("program_registration__user_id"),
            item__program__in=requests.values("program_registration__program_id"),
            item__eligible_for_financial_aid=True,
        ).update(charge_amount=0, purchase_confirmed_on=timezone.now())
        requests.update(reviewed_on=timezone.now(), approved=True)
        return redirect("admin_dashboard")

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
        return reverse_lazy('courses', kwargs={'pk': program_id})


class CourseListView(PermissionRequiredMixin, ListView):
    permission = PermissionType.courses_view_all

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["program_id"] = self.kwargs['pk']
        return context

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return Course.objects.filter(program=program)
