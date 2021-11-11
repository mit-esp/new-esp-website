from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import BaseInlineFormSet, HiddenInput


class CrispyFormMixin(object):
    submit_label = "Save"
    form_action = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_action = self.form_action
        self.helper.add_input(Submit("submit", self.submit_label, css_class="mt-3 w-100"))


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
