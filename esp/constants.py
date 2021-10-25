from django.db.models import IntegerChoices, TextChoices


class ProgramType(TextChoices):
    splash = "splash"
    spark = "spark"
    hssp = "hssp", "HSSP"
    cascade = "cascade"


class RegistrationStep(TextChoices):
    # Edit to add or remove possible registration steps or modify display names
    verify_profile = "verify_profile", "Verify Profile Information"
    submit_waivers = "submit_waivers"
    time_availability = "time_availability"
    lottery_preferences = "lottery_preferences"
    submit_registration = "submit_registration"
    view_assigned_courses = "view_assigned_courses"
    edit_assigned_courses = "edit_assigned_courses"
    pay_program_fees = "pay_program_fees", "Payment"
    complete_surveys = "complete_surveys"


class CourseStatus(TextChoices):
    unreviewed = "unreviewed"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"
    hidden = "hidden"


class CourseRoleType(TextChoices):
    teacher = "teacher"
    observer = "observer"
    student = "student"


class HeardAboutVia(TextChoices):
    teacher = "teacher", "Teacher or Counselor"
    esp_rep = "esp_rep", "ESP representative visited my school"
    parents = "parents"
    friends = "friends"
    poster_at_school = "poster_at_school"
    poster_public = "poster_public", "Poster in some other public place"
    facebook = "facebook"
    newspaper = "newspaper", "Newspaper or Magazine"
    radio_tv = "radio_tv", "Radio or TV"
    attended_other_program = "attended_other_program", "I attended another ESP program"
    attended_last_year = "attended_last_year", "I came to this program last year"
    other = "other", "Other"


class CourseDifficulty(IntegerChoices):
    easy = 1
    moderate = 2
    challenging = 3


class MITAffiliation(TextChoices):
    undergrad = "undergrad", "Undergraduate Student"
    grad = "grad", "Graduate Student"
    postdoc = "postdoc", "Postdoctoral Student"
    other = "other"
    none = ""
