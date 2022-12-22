#######################
Navigating the codebase
#######################

This assumes basic knowledge of Python and preferably some Django.

Models
======

``code/esp/models`` contains several files with model definitions.

Django Panel
============

The Django panel is where direct changes to the data in our databases can be made. On the dev site, it's located at https://esp-dev.mit.edu/django_admin/.

To make a model (object representing information about a course, program, user, etc.) visible on the panel, go to ``code/esp/admin.py`` and register it. For example:

.. code-block:: python

    admin.site.register(course_scheduling_models.ClassroomConstraint)

Templates and views
=====
Webpages on the frontend of the website are defined using a combination of templates and views.

Dashboards
----------
We'll use the admin dashboard as our example here.

Going to ``code/esp/templates/admin/admin_dashboard.html``, we see this block of HTML code:

.. code-block:: python

    <div class="content-wrapper">
        <div class="container-fluid">
            <div class="row">
                <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mt-4">
                        <div class="row">
                        <div class="col-lg-9 col-md-8 col-sm-8 col-8">
                            <h4>Total Users</h4>
                            <h2>{{users_count}}</h2>
                        </div>
                        </div>
                </div>
                <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mt-4">
                        <div class="row">
                        <div class="col-lg-9 col-md-8 col-sm-8 col-8">
                            <h4>Total Students</h4>
                            <h2>{{students_count}}</h2>
                        </div>
                        </div>
                </div>
                <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mt-4">
                        <div class="row">
                        <div class="col-lg-9 col-md-8 col-sm-8 col-8">
                            <h4>Total Teachers</h4>
                            <h2>{{teachers_count}}</h2>
                        </div>
                        </div>
                </div>
                <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mt-4">
                        <div class="row">
                        <div class="col-lg-9 col-md-8 col-sm-8 col-8">
                            <h4>Active Admins</h4>
                            <h2>{{admins_count}}</h2>
                        </div>
                        </div>
                </div>
            </div>
        </div>
        </div>

Each variable wrapped in double curly braces is an attribute of the ``AdminDasboardView`` view, defined in ``code/esp/views/admin_views.py``.

.. code-block:: python

    class AdminDashboardView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.admin_dashboard_view
    template_name = 'admin/admin_dashboard.html'

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

We also have the ability to embed components within our template; for example, the ``program_card`` component included here:

.. code-block:: python

    {% if active_programs %}
    <div class="my-3">
    <div class="row">
        <div class="col-lg-12">
        <h3>Active Programs</h3>
        {% for program in active_programs %}
        {% include "admin/components/program_card.html" %}
        {% endfor %}
        </div>
    </div>
    </div>
    {% endif %}

looks like this in ``code/esp/templates/admin/components/program_card.html``:

.. code-block:: python

    <div class="card card-body my-3">
    <div class="row">
        <div class="col-lg-6">
        <h4>Program <span class="badge rounded-pill bg-secondary">{{ program.name }}</span></h4>
        <p class="my-1 fs-5"><strong>From {{program.start_date}} to {{program.end_date}}</strong></p>
        <p class="my-1 fs-6">Program Stages</p>
        <ol>
        {% for stage in program.stages.all %}
            <li>Stage {{ stage.name }}: {{ stage.start_date|date:"m/d/Y" }} - {{ stage.end_date|date:"m/d/Y" }} <a href="{% url "update_program_stage" pk=stage.id %}"><span class="bi-pencil"></span></a></li>
            <ul>{% for step in stage.steps.all %}<li>{{ step.get_step_key_display }}</li>{% endfor %}</ul>
        {% empty %}
            None Created
        {% endfor %}
        </ol>
        <p class="my-0"><strong>Program Last Updated</strong>: {{ program.updated_on }} <a class="btn btn-outline-success my-2 mx-2" href='{% url "update_program" program.id %}'>Update</a>
    </p>

        </div>
        <div class="col-lg-6">
        <div class="card">
            <div class="card-body">
            <h5 class="card-title">Admin actions</h5>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'manage_students' pk=program.id %}">Manage Students</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'manage_teachers' pk=program.id %}">Manage Teachers</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'courses' pk=program.id %}">Manage Courses</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'manage_classroom_availability' pk=program.id %}">Manage Classroom Availability</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'scheduler' %}?program_id={{program.id}} ">The Scheduler</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'program_lottery' pk=program.id %}">Run Lottery</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'approve_financial_aid' pk=program.id %}">Approve Financial Aid Requests</a>
            <a class="btn btn-outline-success mx-1 my-1" role="button" href="{% url 'print_student_schedules' pk=program.id %}" target="_blank">Print Student Schedules</a>
            </div>
        </div>
        </div>
    </div>
    </div>

We can also refer to particular pages by name instead of url, passing in formatting arguments as needed. These names are defined in ``code/esp/urls.py``, which associates webpage paths with views and unique names/labels. For example, the above code for ``program_card`` refers to the url ``'manage_students'``, which is defined as 

.. code-block:: python

    path('admin/programs/<uuid:pk>/manage/students/', AdminManageStudentsView.as_view(),
         name="manage_students")

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

The ``create_program_stage`` label in this code comes from ``code/esp/urls.py``.

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
