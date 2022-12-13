#######################
Navigating the codebase
#######################

This assumes basic knowledge of Python and preferably some Django.

Django Panel
============

The Django panel is where direct changes to the data in our databases can be made. On the dev site, it's located at https://esp-dev.mit.edu/django_admin/.

To make a model (object representing information about a course, program, user, etc.) visible on the panel, go to ``code/esp/admin.py`` and register it. For example:

.. code-block:: python

    admin.site.register(course_scheduling_models.ClassroomConstraint)

Views
=====

Dashboards
----------

Forms
-----

We'll use the “Create Program” form as our example form. This form creates an instance of the Program model and links to a form that creates ProgramStages.

The proper form is in ``code/esp/forms.py``. It takes particular fields from the ``Program`` model and creates inputs for each one. Specific input styles can be specified in the widgets parameter.

.. code-block:: python

    class ProgramForm(CrispyFormMixin, ModelForm):
        submit_kwargs = {"onclick": "return confirm('Are you sure?')"}

        def __init__(self, *args, submit_label="Create Program", **kwargs):
            self.submit_label = submit_label
            super().__init__(*args, **kwargs)

        class Meta:
            model = Program
            # These fields are labelled by turning underscores to spaces and capitalizing.
            fields = [
                "name", "program_type", "start_date", "end_date", "number_of_weeks", "time_block_minutes",
                "min_grade_level", "max_grade_level", "description", "notes"
            ]
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            }


This form is called in ``code/esp/views/admin_views.py`` as the ``ProgramCreateView`` class. This defines the navigation information for this form.

.. code-block:: python

    class ProgramCreateView(PermissionRequiredMixin, CreateView):
        permission = PermissionType.admin_dashboard_actions
        model = Program
        form_class = ProgramForm
        template_name = 'admin/program_form.html'

        def form_valid(self, form):
            next_link = super().form_valid(form)
            return next_link

        # next page
        def get_success_url(self):
            return reverse_lazy('create_program_stage', kwargs={"pk": self.object.id})

The ``create_program_stage`` label in this code comes from ``code/esp/urls.py``, which associates webpage paths with views and unique names/labels.

.. code-block:: python
    path('admin/programs/uuid:pk/stages/create/', ProgramStageCreateView.as_view(), name="create_program_stage")

Finally, the HTML that displays this form is defined as a template in ``code/esp/templates/admin/program_form.html``:

.. code-block:: python

    {% extends "base_templates/base.html" %}
    {% load crispy_forms_tags %}
    {% block head %}{% endblock %}
    {% block title %}Program{% endblock %}

    {% block body %}
    <h1>Programs</h1>
    <div class="col-sm-6">
    {% crispy form %}
    </div>
    {% endblock %}

    {% block script %}
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script>
    </script>
    {% endblock %}
