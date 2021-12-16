from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import FieldError, ValidationError
from django.db import transaction
from django.forms import ModelForm, inlineformset_factory

from common.constants import (REGISTRATION_USER_TYPE_CHOICES, GradeLevel,
                              USStateEquiv)
from common.forms import (CrispyFormMixin, HiddenOrderingInputFormset,
                          MultiFormMixin)
from common.models import User
from esp.constants import (CourseDifficulty, CourseTagCategory,
                           StudentRegistrationStepType,
                           TeacherRegistrationStepType)
from esp.models.course_scheduling_models import (ClassroomTimeSlot,
                                                 CourseSection)
from esp.models.program_models import Course, CourseTag, Program, ProgramStage
from esp.models.program_registration_models import (ProgramRegistrationStep,
                                                    StudentProfile,
                                                    TeacherProfile,
                                                    TeacherRegistration)
from esp.serializers import AssignClassroomTimeSlotSerializer


class RegisterUserForm(CrispyFormMixin, UserCreationForm):
    submit_label = "Create New Account"

    email = forms.EmailField(
        label="Email Address", required=True, max_length=300, help_text='Enter a valid email address.'
    )
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    phone_number = forms.CharField(
        label="Phone Number", required=True, max_length=32, help_text="Enter a valid phone number."
    )
    user_type = forms.ChoiceField(
        choices=REGISTRATION_USER_TYPE_CHOICES, label="Account Type", required=True,
        help_text="What kind of account do you want to create?"
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'phone_number',
            'user_type',
        ]


class StudentProfileForm(CrispyFormMixin, ModelForm):
    class Meta:
        model = StudentProfile
        exclude = ["user"]
        labels = {
            "heard_about_esp_other_detail": "",
        }


class UpdateStudentProfileForm(StudentProfileForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["graduation_year"].disabled = True
        self.helper.layout = layout.Layout(
            layout.Layout(*self.helper.layout[-3:]),
            layout.Layout(*self.helper.layout[:-3])
        )


class TeacherProfileForm(CrispyFormMixin, ModelForm):
    class Meta:
        model = TeacherProfile
        exclude = [
            "user",
        ]


class UpdateTeacherProfileForm(TeacherProfileForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = layout.Layout(
            layout.Layout(*self.helper.layout[-3:]),
            layout.Layout(*self.helper.layout[:-3])
        )


class ProgramForm(CrispyFormMixin, ModelForm):
    submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

    def __init__(self, *args, submit_label="Create Program", **kwargs):
        self.submit_label = submit_label
        super().__init__(*args, **kwargs)

    class Meta:
        model = Program
        fields = [
            "name", "program_type", "start_date", "end_date", "number_of_weeks", "time_block_minutes",
            "min_grade_level", "max_grade_level", "description", "notes"
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
        }


class ProgramStageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = ProgramStage
        fields = ("name", "start_date", "end_date", "description")
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
        }


ProgramRegistrationStepFormset = inlineformset_factory(
    ProgramStage, ProgramRegistrationStep, can_order=True, formset=HiddenOrderingInputFormset,
    fields=("step_key", "display_name", "description"),
    labels=({"step_key": "Step Type", "display_name": "Alternate display name"}),
    widgets=({"description": forms.Textarea(attrs={"rows": 1})})
)


class TeacherCourseForm(CrispyFormMixin, ModelForm):
    submit_label = "Create Class"

    categories = forms.ModelMultipleChoiceField(
        queryset=CourseTag.objects.filter(tag_category=CourseTagCategory.course_category),
        help_text="Hold down “Control”, or “Command” on a Mac, to select more than one."
    )
    additional_tags = forms.ModelMultipleChoiceField(
        queryset=CourseTag.objects.exclude(
            tag_category=CourseTagCategory.course_category
        ).filter(editable_by_teachers=True),
        blank=True,
    )

    class Meta:
        model = Course
        fields = [
            "name",
            "description",
            "max_section_size",
            "max_sections",
            "time_slots_per_session",
            "number_of_weeks",
            "sessions_per_week",
            "prerequisites",
            "min_grade_level",
            "max_grade_level",
            "difficulty",
            "teacher_notes",
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
        }

    def __init__(self, *args, is_update=False, program=None, **kwargs):
        if is_update:
            self.submit_label = "Update class"
        super().__init__(*args, **kwargs)
        if not self.fields["additional_tags"].queryset.exists():
            self.fields.pop("additional_tags")
        if not is_update:
            self.helper.add_input(layout.Submit("add_another", "Save and add another", css_class="mt-2"))
        self.fields["time_slots_per_session"].help_text = f"Time slots are {program.time_block_minutes} minutes long."
        program_grade_levels = [
            choice for choice in GradeLevel.choices if program.max_grade_level >= choice[0] >= program.min_grade_level
        ]
        self.fields["min_grade_level"].choices = program_grade_levels
        self.fields["max_grade_level"].choices = program_grade_levels

    def save(self, commit=True):
        categories = self.cleaned_data.pop("categories")
        additional_tags = self.cleaned_data.pop("additional_tags", [])
        instance = super().save(commit)
        instance.tags.add(*categories, *additional_tags)


class TeacherRegistrationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user.__str__()


class AddCoTeacherForm(CrispyFormMixin, forms.Form):
    submit_label = "Add Co-teacher"
    teacher = TeacherRegistrationChoiceField(queryset=None)

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = TeacherRegistration.objects.exclude(
            id__in=course.teachers.values("teacher_registration_id")
        ).filter(
            program_id=course.program_id, availabilities__isnull=False
        ).distinct()


class QuerySendEmailForm(MultiFormMixin, forms.Form):
    submit_label = "Send"
    submit_name = "query_form"
    query = forms.CharField(
        label='Query',
        widget=forms.TextInput(
            attrs={'placeholder': 'user_type=student, registrations__completed_steps__step=edit_assigned_courses'}
        )
    )
    subject = forms.CharField(label='Subject Line')
    body = forms.CharField(label='Email Body', widget=forms.Textarea(
        attrs={
            'placeholder':
            'Hello {{ first_name }} {{ last_name }}, your account {{ username }} has not yet paid registration fees...'
        })
    )

    def clean_query(self):
        query = self.cleaned_data['query'].replace(' ', '')
        try:
            kwargs = {}
            for arg in query.split(','):
                x, y = arg.split('=')
                kwargs[x] = y
            to_users = User.objects.filter(**kwargs)
        except (FieldError, ValueError) as e:
            print('ERROR: ', e)
            raise ValidationError(e)
        self.cleaned_data["users"] = to_users
        return kwargs


class TeacherSendEmailForm(MultiFormMixin, forms.Form):
    submit_label = "Send"
    submit_name = "teacher_form"
    program = forms.ModelChoiceField(queryset=Program.objects.all())
    submit_one_class = forms.BooleanField(required=False, label='Submitted at least one class')
    difficulty = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), *CourseDifficulty.choices],
        label='Teaches a course of a certain difficulty'
    )
    registration_step = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), *TeacherRegistrationStepType.choices], label='Completed this registration step'
    )

    subject = forms.CharField(label='Subject Line')
    body = forms.CharField(
        label='Email Body',
        widget=forms.Textarea(attrs={
            'placeholder': 'Hello {{ first_name }} {{ last_name }}, your account {{ username }} has an updated...'
        }))


class StudentSendEmailForm(MultiFormMixin, forms.Form):
    submit_label = "Send"
    submit_name = "student_form"
    only_guardians = forms.BooleanField(
        required=False,
        label='Send emails only to guardians',
        help_text='Note: this will also change first_name, last_name, and email merge fields'
    )
    program = forms.ModelChoiceField(queryset=Program.objects.all())
    registration_step = forms.ChoiceField(
        required=False, choices=[('', '---------'), *StudentRegistrationStepType.choices],
        label='Completed this registration step'
    )

    subject = forms.CharField(label='Subject Line')
    body = forms.CharField(
        label='Email Body',
        widget=forms.Textarea(attrs={
            'placeholder': 'Hello {{ first_name }} {{ last_name }}, your account {{ username }} has an updated...'
        })
    )


class AssignClassroomTimeSlotsForm(forms.Form):
    data = forms.JSONField()

    def clean_data(self):
        """
        Validate data json structure.
        """
        data = self.cleaned_data["data"]
        serializer = AssignClassroomTimeSlotSerializer(data=data, many=True)
        if not serializer.is_valid():
            # Todo: Add sentry notification; this error is not intended for the user
            raise ValidationError("Sorry, something went wrong")
        self._validate_ids(ClassroomTimeSlot, 'classroom_time_slot_id', serializer.data)
        self._validate_ids(CourseSection, 'course_section_id', serializer.data, ignore_none=True)
        return serializer.data

    def save(self):
        """
        Save ClassroomTimeSlot assignments. This is intentionally not optimized for readability since
        we don't expect any single call to affect that many ClassroomTimeSlot objects.
        """
        with transaction.atomic():
            for datum in self.cleaned_data["data"]:
                (
                    ClassroomTimeSlot.objects
                    .filter(id=datum["classroom_time_slot_id"])
                    .update(course_section_id=datum["course_section_id"])
                )

    def _validate_ids(self, Model, id_field_name, data, ignore_none=False):
        model_ids = [datum.get(id_field_name, None) for datum in data]
        if ignore_none:
            model_ids = [_id for _id in model_ids if _id is not None]
        model_count = Model.objects.filter(id__in=[_id for _id in model_ids if _id is not None]).count()
        if len(set(model_ids)) != model_count:
            # Todo: Add sentry notification; this error is not intended for the user
            raise ValidationError("Sorry, something went wrong")


class PaymentForm(CrispyFormMixin, forms.Form):
    submit_label = "Confirm payment"

    card_number = forms.CharField()
    expiration_date = forms.CharField()
    cvc_code = forms.CharField(max_length=3, min_length=3, label="CVC Code")
    name_on_card = forms.CharField()
    line_1 = forms.CharField()
    line_2 = forms.CharField()
    city = forms.CharField()
    state = forms.ChoiceField(choices=USStateEquiv.choices)
    zipcode = forms.CharField(max_length=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                "Credit Card Info",
                "card_number",
                layout.Div(
                    layout.Div("expiration_date", css_class="me-4"),
                    layout.Field("cvc_code"),
                    css_class="d-flex"
                )
            ),
            layout.Fieldset(
                "Billing Address",
                "line_1",
                "line_2",
                layout.Div(
                    layout.Field("city"),
                    layout.Field("state"),
                    layout.Field("zipcode"),
                    css_class="d-flex justify-content-between"
                )
            )
        )

    def clean_card_number(self, value):
        # TODO
        return value
