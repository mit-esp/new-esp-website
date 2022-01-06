from datetime import date

from django.db import models
from django.db.models import Exists, Min, OuterRef, Sum, Value
from django.db.models.functions import Now
from django.utils import timezone

from common.constants import GradeLevel, ShirtSize, UserType, USStateEquiv
from common.models import BaseModel, User
from esp.constants import HeardAboutVia, MITAffiliation, PaymentMethod
from esp.models.course_scheduling_models import CourseSection
from esp.models.program_models import (Course, ExternalProgramForm,
                                       PreferenceEntryCategory, Program,
                                       ProgramRegistrationStep,
                                       PurchaseableItem,
                                       TeacherProgramRegistrationStep,
                                       TimeSlot)
from esp.validators import validate_graduation_year

####################################################
# STUDENT REGISTRATIONS
####################################################


class StudentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="student_profile")
    address_street = models.CharField(max_length=512)
    address_city = models.CharField(max_length=512)
    address_state = models.CharField(choices=USStateEquiv.choices, max_length=16)
    address_zip = models.CharField(max_length=10)

    home_phone = models.CharField(max_length=16)
    cell_phone = models.CharField(max_length=16, null=True, blank=True)

    dob = models.DateField()
    graduation_year = models.IntegerField(validators=[validate_graduation_year])
    school = models.CharField(max_length=512)
    heard_about_esp_via = models.CharField(
        choices=HeardAboutVia.choices, max_length=32, verbose_name="How did you hear about this program?",
        help_text="If you select 'Other', please provide detail in the text box."
    )
    heard_about_esp_other_detail = models.CharField(max_length=1024, null=True, blank=True)

    guardian_first_name = models.CharField(max_length=128)
    guardian_last_name = models.CharField(max_length=128)
    guardian_email = models.EmailField()
    guardian_home_phone = models.CharField(max_length=16)
    guardian_cell_phone = models.CharField(max_length=16, null=True, blank=True)

    emergency_contact_first_name = models.CharField(max_length=128)
    emergency_contact_last_name = models.CharField(max_length=128)
    emergency_contact_email = models.EmailField()
    emergency_contact_address_street = models.CharField(max_length=512)
    emergency_contact_address_city = models.CharField(max_length=512)
    emergency_contact_address_state = models.CharField(choices=USStateEquiv.choices, max_length=16)
    emergency_contact_address_zip = models.CharField(max_length=10)
    emergency_contact_home_phone = models.CharField(max_length=16)
    emergency_contact_cell_phone = models.CharField(max_length=16, null=True, blank=True)

    def grade_level(self):
        current_date = timezone.now().date()
        # Assumes graduation on July 1
        years_until_graduation = int((date(year=int(self.graduation_year), month=7, day=1) - current_date).days/365)
        return 12 - years_until_graduation

    def get_grade_level_display(self):
        grade_level = self.grade_level()
        if grade_level > 12:
            return "Graduated"
        return GradeLevel(grade_level).label


class ProgramRegistration(BaseModel):
    """ProgramRegistration represents a user's registration for a program."""
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")
    completed_forms = models.ManyToManyField(
        ExternalProgramForm, related_name="completed_student_registrations", through="CompletedStudentForm"
    )
    allow_early_registration_after = models.DateTimeField(null=True)  # Overrides deadlines set on program stages
    allow_late_registration_until = models.DateTimeField(null=True)  # Overrides deadlines set on program stages
    checked_in = models.BooleanField(default=False)

    class Meta:
        unique_together = [("program_id", "user_id")]

    def get_program_stage(self):
        active_stages = (
            self.program.stages.filter(start_date__lte=Now(), end_date__gte=Now())
            if not self.ignore_registration_deadlines() else self.program.stages.all()
        )
        if not active_stages.exists():
            return None
        completed_steps = self.completed_steps.values_list("step_id", flat=True)
        incomplete_stages = active_stages.filter(
            Exists(ProgramRegistrationStep.objects
                   .filter(program_stage_id=OuterRef('id'), required_for_stage_completion=True)
                   .exclude(id__in=completed_steps))
        )
        if incomplete_stages.exists():
            return incomplete_stages.first()
        return active_stages.last()

    def ignore_registration_deadlines(self):
        return (
                (self.allow_early_registration_after and self.allow_early_registration_after < timezone.now())
                or (self.allow_late_registration_until and self.allow_late_registration_until > timezone.now())
        )

    def get_barcode_id(self):
        return "".join((str(self.id)).split('-')).upper()

    def get_amount_owed(self):
        return self.user.purchases.filter(
            item__program=self.program,
            purchase_confirmed_on__isnull=True
        ).aggregate(Sum("charge_amount"))["charge_amount__sum"]

    def check_registration_requirements(self):
        return_dict = {
            "requirements_satisfied": True,
            "errors": [],
        }
        if self.incomplete_forms().exists():
            return_dict["requirements_satisfied"] = False
            return_dict["errors"].append("Not all program forms have been completed.")
        if not self.all_required_purchases_complete():
            return_dict["requirements_satisfied"] = False
            return_dict["errors"].append("Not all required payments have been made.")
        amount_owed = self.get_amount_owed()
        if amount_owed:
            return_dict["requirements_satisfied"] = False
            return_dict["errors"].append(f"Payment (${amount_owed}) is still owed for items in cart.")
        return return_dict

    def incomplete_forms(self):
        return self.program.external_forms.filter(user_type=UserType.student).annotate(
            completed=Exists(
                self.completed_forms_extra.filter(form_id=OuterRef("id"), completed_on__isnull=False)
            )
        ).filter(completed=False)

    def all_required_purchases_complete(self):
        return not self.program.purchase_items.filter(required_for_registration=True).annotate(
            purchased=Exists(
                self.user.purchases.filter(item_id=OuterRef("id"), purchase_confirmed_on__isnull=False)
            )
        ).filter(purchased=False).exists()

    def __str__(self):
        return f"{self.program} registration for {self.user}"


class CompletedRegistrationStep(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="completed_steps", on_delete=models.PROTECT)
    step = models.ForeignKey(ProgramRegistrationStep, related_name="registrations", on_delete=models.PROTECT)
    completed_on = models.DateTimeField()


class StudentAvailability(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="availabilities", on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeSlot, related_name="student_availabilities", on_delete=models.PROTECT)


class ClassPreference(BaseModel):
    """ClassPreference represents a preference entry category that a user has applied to a class section."""
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    course_section = models.ForeignKey(CourseSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)
    value = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.registration} - {self.category} preference"


class ClassRegistration(BaseModel):
    course_section = models.ForeignKey(CourseSection, related_name="registrations", on_delete=models.PROTECT)
    program_registration = models.ForeignKey(
        ProgramRegistration, related_name="class_registrations", on_delete=models.PROTECT
    )
    created_by_lottery = models.BooleanField()
    confirmed_on = models.DateTimeField(null=True)


class UserPayment(BaseModel):
    user = models.ForeignKey(User, related_name="payments", on_delete=models.PROTECT)
    payment_method = models.CharField(choices=PaymentMethod.choices, max_length=64)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    vendor_authorization_id = models.CharField(max_length=124, null=True)
    transaction_datetime = models.DateTimeField()


class FinancialAidRequest(BaseModel):
    program_registration = models.ForeignKey(
        ProgramRegistration, related_name="financial_aid_requests", on_delete=models.PROTECT)
    reduced_lunch = models.BooleanField(
        verbose_name="Do you receive free/reduced lunch at school?", blank=True, default=False
    )
    household_income = models.CharField(
        verbose_name="Approximately what is your household income (round to the nearest $10,000)?", null=True,
        blank=True,
        max_length=12
    )
    student_comments = models.TextField(
        verbose_name="Please describe in detail your financial situation this year.",
        null=True, blank=True
    )
    student_prepared = models.BooleanField(
        verbose_name="Did anyone besides the student fill out any portions of this form?", blank=True, default=False
    )
    approved = models.BooleanField(default=False)
    reviewer_comments = models.TextField(null=True)
    reviewed_on = models.DateTimeField(null=True)


class PurchaseLineItem(BaseModel):
    user = models.ForeignKey(User, related_name="purchases", on_delete=models.PROTECT)
    item = models.ForeignKey(PurchaseableItem, related_name="purchases", on_delete=models.PROTECT)
    payment = models.ForeignKey(UserPayment, related_name="line_items", on_delete=models.PROTECT, null=True)
    added_to_cart_on = models.DateTimeField()
    purchase_confirmed_on = models.DateTimeField(null=True)
    charge_amount = models.DecimalField(max_digits=6, decimal_places=2)


class CompletedForm(BaseModel):
    form = models.ForeignKey(ExternalProgramForm, on_delete=models.PROTECT, related_name="+")
    completed_on = models.DateTimeField(null=True)
    integration_id = models.CharField(max_length=256, null=True)


class CompletedStudentForm(CompletedForm):
    program_registration = models.ForeignKey(
        ProgramRegistration, on_delete=models.PROTECT, related_name="completed_forms_extra"
    )

#####################################################
# TEACHER REGISTRATIONS
#####################################################


class TeacherProfile(BaseModel):
    user = models.OneToOneField(User, related_name="teacher_profile", on_delete=models.PROTECT)
    cell_phone = models.CharField(max_length=16)
    mit_affiliation = models.CharField(
        choices=MITAffiliation.choices, max_length=32, verbose_name="What is your affiliation with MIT?"
    )
    major = models.CharField(
        max_length=128, blank=True, null=True,
        help_text="If you are currently a student, please provide your major or degree field."
    )
    graduation_year = models.IntegerField(
        null=True, blank=True, validators=[validate_graduation_year],
        help_text="If you are currently a student, please provide your graduation year."
    )
    university_or_employer = models.CharField(
        max_length=128, blank=True, null=True,
        help_text="If you are not affiliated with MIT, please provide your university or employer."
    )
    bio = models.TextField(blank=True, null=True)
    shirt_size = models.CharField(max_length=3, choices=ShirtSize.choices)


class TeacherRegistration(BaseModel):
    program = models.ForeignKey(Program, related_name="teacher_registrations", on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="teacher_registrations", on_delete=models.PROTECT)
    courses = models.ManyToManyField(Course, related_name="teacher_registrations", through="CourseTeacher")
    completed_forms = models.ManyToManyField(
        ExternalProgramForm, related_name="completed_teacher_registrations", through="CompletedTeacherForm"
    )
    allow_early_registration_after = models.DateTimeField(null=True)  # Overrides deadlines set on program stages
    allow_late_registration_until = models.DateTimeField(null=True)  # Overrides deadlines set on program stages
    checked_in_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = [("program_id", "user_id")]

    def __str__(self):
        return f"{self.program} teaching registration for {self.user}"

    def visible_registration_steps(self):
        steps = self.program.teacher_registration_steps.all()
        if not self.ignore_registration_deadlines():
            steps = steps.filter(access_start_date__lt=timezone.now(), access_end_date__gt=timezone.now())
        completed_steps = self.completed_steps.values("step_id")
        visible_steps = steps.filter(
            id__in=completed_steps, display_after_completion=True
        ).annotate(completed=Value(True))
        if self.completed_steps.count() < steps.count():
            first_incomplete_required_step = steps.exclude(
                id__in=completed_steps
            ).filter(required_for_next_step=True).aggregate(Min("_order"))["_order__min"]
            visible_incomplete_steps = steps.exclude(
                id__in=completed_steps
            ).filter(_order__lte=first_incomplete_required_step).annotate(completed=Value(False))
            visible_steps = visible_steps | visible_incomplete_steps
        return visible_steps.order_by("_order")

    def has_access_to_step(self, step):
        return (
            step.id not in self.completed_steps.values("step_id")
            or step.allow_changes_after_completion
        ) and step in self.visible_registration_steps()

    def ignore_registration_deadlines(self):
        return (
            (self.allow_early_registration_after and self.allow_early_registration_after < timezone.now())
            or (self.allow_late_registration_until and self.allow_late_registration_until > timezone.now())
        )

    def check_registration_requirements(self):
        return_dict = {
            "requirements_satisfied": True,
            "errors": [],
        }
        if not self.all_program_forms_complete():
            return_dict["requirements_satisfied"] = False
            return_dict["errors"].append("Not all program forms have been completed.")
        return return_dict

    def all_program_forms_complete(self):
        return self.program.external_forms.filter(user_type=UserType.teacher).annotate(
            completed=Exists(
                self.completed_forms_extra.filter(form_id=OuterRef("id"), completed_on__isnull=False)
            )
        ).filter(completed=False).exists()


class CompletedTeacherRegistrationStep(BaseModel):
    registration = models.ForeignKey(TeacherRegistration, related_name="completed_steps", on_delete=models.PROTECT)
    step = models.ForeignKey(TeacherProgramRegistrationStep, related_name="registrations", on_delete=models.PROTECT)
    completed_on = models.DateTimeField()


class CourseTeacher(BaseModel):
    course = models.ForeignKey(Course, related_name="course_teachers", on_delete=models.PROTECT)
    teacher_registration = models.ForeignKey(
        TeacherRegistration, related_name="course_teachers", on_delete=models.PROTECT
    )
    is_course_creator = models.BooleanField()
    confirmed_on = models.DateTimeField(null=True)


class TeacherAvailability(BaseModel):
    registration = models.ForeignKey(TeacherRegistration, related_name="availabilities", on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeSlot, related_name="teacher_availabilities", on_delete=models.PROTECT)


class CompletedTeacherForm(CompletedForm):
    teacher_registration = models.ForeignKey(
        TeacherRegistration, on_delete=models.PROTECT, related_name="completed_forms_extra"
    )
