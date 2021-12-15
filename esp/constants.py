from django.db.models import IntegerChoices, TextChoices


class ProgramType(TextChoices):
    splash = "splash"
    spark = "spark"
    hssp = "hssp", "HSSP"
    cascade = "cascade"


class StudentRegistrationStepType(TextChoices):
    # Edit to add or remove possible student registration steps or modify display names
    verify_profile = "verify_profile", "Verify Profile Information"
    submit_waivers = "submit_waivers"
    time_availability = "time_availability"
    lottery_preferences = "lottery_preferences"
    submit_registration = "submit_registration"
    confirm_assigned_courses = "view_assigned_courses"
    pay_program_fees = "pay_program_fees", "Payment"
    complete_surveys = "complete_surveys"


class TeacherRegistrationStepType(TextChoices):
    verify_profile = "teacher_verify_profile"
    submit_waivers = "teacher_submit_waiver"
    submit_minors_policy_acknowledgement = "teacher_minors_policy"
    time_availability = "teacher_time_availability"
    submit_courses = "teacher_submit_courses"
    confirm_course_schedule = "teacher_confirm_course_schedule"


class CourseStatus(TextChoices):
    unreviewed = "unreviewed"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"
    hidden = "hidden"


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


class ProgramTagCategory(TextChoices):
    other = "other"


class CourseTagCategory(TextChoices):
    course_category = "course_category"
    other = "other"


class ClassroomTagCategory(TextChoices):
    location = "location"
    resource = "resource"
    other = "other"


class PaymentMethod(TextChoices):
    card_online = "card_online"
    card_in_person = "card_in_person"
    cash = "cash"
