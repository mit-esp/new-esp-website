from crispy_forms.tests.forms import SampleForm
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView

# from common.forms import FileUploadForm


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


# class FileUploadView(FormView):
#     template_name = "portal/upload_file.html"
#     http_method_names = ["get", "post"]
#     form_class = FileUploadForm
# 
#     def form_valid(self, form):
#         form.save(self.request.user)
#         messages.success(self.request, "File successfully uploaded.")
#         return self.render_to_response(self.get_context_data())


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm
