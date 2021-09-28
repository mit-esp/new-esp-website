from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class CrispyFormMixin(object):
    submit_label = "Save"
    form_action = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = self.form_action
        self.helper.add_input(Submit("submit", self.submit_label))


# from common.models import UploadFile
# class FileUploadForm(CrispyFormMixin, forms.ModelForm):
#     file = forms.FileField(label="Upload a file")
#
#     submit_label = "Upload"
#     form_action = "upload_file"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def save(self, user):
#         file_file = super().save(commit=False)
#         file_file.user = user
#         file_file.save()
#
#     class Meta:
#         model = UploadFile
#         fields = ["file"]
