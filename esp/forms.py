from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from common.constants import UserType
from common.forms import CrispyFormMixin
from common.models import User
from esp.models import Class, Program


class RegisterForm(CrispyFormMixin, UserCreationForm):
    submit_label = "Create Account"

    email = forms.EmailField(label="Email Address", required=True, max_length=300, help_text='Enter a valid email address.')
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    phone_number = forms.CharField(label="Phone Number", required=True, max_length=32, help_text="Enter a valid phone number.")
    user_type = forms.ChoiceField(choices=UserType.choices, label="Account Type", required=True, help_text="What kind of account do you want to create?")

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


class ProgramForm(CrispyFormMixin, ModelForm):
    submit_label = "Create Program"
    submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

    class Meta:
        model = Program
        fields = ["name", "start_date", "end_date", "description", "notes"]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class ClassForm(CrispyFormMixin, ModelForm):
    submit_label = "Create Class"
    submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

    class Meta:
        model = Class
        fields = ["name", "start_date", "end_date", "description", "notes", "max_size", "prerequisites"]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }
