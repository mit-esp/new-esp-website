from django.db.models import TextChoices


class ProgramType(TextChoices):
    splash = "splash"
    spark = "spark"
    hssp = "hssp", "HSSP"
    cascade = "cascade"


class RegistrationStep(TextChoices):
    # Edit to add or remove possible registration steps or display names
    verify_profile = "verify_profile", "Verify Profile Information"
    submit_waivers = "submit_waivers"
    time_availability = "time_availability"
    lottery_preferences = "lottery_preferences"
    submit_registration = "submit_registration"
    view_assigned_classes = "view_assigned_classes"
    edit_assigned_classes = "edit_assigned_classes"
    pay_program_fees = "pay_program_fees", "Payment"
    check_in = "check_in"
    program_started = "program_started"
    program_ended = "program_ended"
