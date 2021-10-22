from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, inlineformset_factory

from common.constants import REGISTRATION_USER_TYPE_CHOICES
from common.forms import CrispyFormMixin, HiddenOrderingInputFormset
from common.models import User
from esp.models.program import Course, Program, ProgramStage
from esp.models.program_registration import (ProgramRegistrationStep,
                                             StudentProfile, TeacherProfile)


class RegisterUserForm(CrispyFormMixin, UserCreationForm):
    submit_label = "Create Account"

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
        self.helper.layout = layout.Layout(
            layout.Layout(*self.helper.layout[-3:]),
            layout.Layout(*self.helper.layout[:-3])
        )
        self.helper["graduation_year"].wrap(layout.Field, disabled=True)


class TeacherProfileForm(CrispyFormMixin, ModelForm):
    class Meta:
        model = TeacherProfile
        exclude = [
            "user",
        ]


class ProgramForm(CrispyFormMixin, ModelForm):
    submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

    def __init__(self, *args, submit_label="Create Program", **kwargs):
        self.submit_label = submit_label
        super().__init__(*args, **kwargs)

    class Meta:
        model = Program
        fields = ["name", "program_type", "start_date", "end_date", "description", "notes"]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
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
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


ProgramRegistrationStepFormset = inlineformset_factory(
    ProgramStage, ProgramRegistrationStep, can_order=True, formset=HiddenOrderingInputFormset,
    fields=("step_key", "display_name", "description"),
    labels=({"step_key": "Step Type", "display_name": "Alternate display name"}),
    widgets=({"description": forms.Textarea(attrs={"rows": 1})})
)


class CourseForm(CrispyFormMixin, ModelForm):
    submit_label = "Create Class"
    submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

    class Meta:
        model = Course
        fields = ["name", "start_date", "end_date", "description", "notes", "max_size", "prerequisites"]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }
