from urllib.parse import urlparse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.forms import BaseInlineFormSet, HiddenInput, ModelForm
from django.urls import NoReverseMatch, resolve, reverse

from common.models import SiteRedirectPath


class CrispyFormMixin(object):
    submit_label = "Save"
    submit_name = "submit"
    form_action = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_action = self.form_action
        self.helper.add_input(Submit(self.submit_name, self.submit_label, css_class="mt-3 w-100"))


class MultiFormMixin(CrispyFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append('multiform_key')


class HiddenOrderingInputFormset(BaseInlineFormSet):
    ordering_widget = HiddenInput

    def clean(self):
        super().clean()
        order = 0
        for form in self.forms:
            form.instance._order = order
            order += 1


class CrispyFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_style = "inline"
        self.form_class = "form-inline"
        self.template = "bootstrap4/table_inline_formset.html"


class SiteRedirectPathForm(ModelForm):
    class Meta:
        model = SiteRedirectPath
        fields = [
            "path",
            "redirect_url_name",
            "redirect_full_url",
        ]

    def clean_path(self):
        path = self.cleaned_data["path"].strip("/")
        match = resolve(f"/{path}/")
        if match.url_name != "site_redirect":
            raise ValidationError(f"{path} already exists")
        return path

    def clean_redirect_url_name(self):
        redirect_url_name = self.cleaned_data.get("redirect_url_name")
        if not redirect_url_name:
            return
        try:
            reverse(redirect_url_name)
        except NoReverseMatch:
            raise ValidationError("Invalid url name")
        return redirect_url_name

    def clean_redirect_full_url(self):
        url = self.cleaned_data.get("redirect_full_url")
        split_url = urlparse(url)
        print(split_url)
        if not split_url.hostname:
            if not split_url.path:
                raise ValidationError("Enter valid URL")
            return f"/{url.lstrip('/')}"
        return URLValidator()(url)

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get("redirect_url_name") or cleaned_data.get("redirect_full_url")):
            raise ValidationError("Set either a redirect URL name or full URL.")
        return cleaned_data
