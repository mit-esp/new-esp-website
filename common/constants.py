from django.db.models import IntegerChoices, TextChoices


class UserType(TextChoices):
    admin = "admin"
    teacher = "teacher", "Volunteer Teacher"
    student = "student", "Student (Grade 7-12)"
    guardian = "guardian", "Guardian of Student"
    onsite_volunteer = "onsite_volunteer", "On-site Volunteer"


# Restrict registration form to non-admin user types
REGISTRATION_USER_TYPE_CHOICES = [
    (UserType.student, UserType.student.label),
    (UserType.teacher, UserType.teacher.label),
    (UserType.guardian, UserType.guardian.label),
    (UserType.onsite_volunteer, UserType.onsite_volunteer.label),
]


class PermissionType(TextChoices):
    """To add a new permission to a particular user type, modify the permissions lists in common/auth.py"""
    # WIP: permissions list TBD

    # Admin actions
    courses_edit_all = "edit_courses"
    courses_view_all = "view_courses"
    programs_edit_all = "edit_programs"
    programs_view_all = "view_all_programs"
    admin_dashboard_view = "view_admin_dashboard"
    student_registrations_edit_all = "student_registrations_view_all"
    teacher_registrations_edit_all = "teacher_registrations_edit_all"
    student_profiles_edit_all = "student_profiles_edit_all"
    teacher_profiles_edit_all = "teacher_profiles_edit_all"

    # Student actions
    student_create_profile = "create_student_profile"
    student_dashboard_view = "view_student_dashboard"
    student_register_for_program = "student_register_for_program"
    student_update_profile = "student_update_profile"

    # Teacher actions
    teacher_dashboard_view = "view_teacher_dashboard"
    teacher_create_profile = "create_teacher_profile"
    teacher_update_profile = "update_teacher_profile"
    teacher_register_for_program = "teacher_register_for_program"
    teacher_edit_own_courses = "teacher_edit_own_courses"

    # Volunteer actions
    volunteer_program_dashboard_view = "view_volunteer_dashboard"
    volunteer_register_for_program = "volunteer_register_for_program"


class GradeLevel(IntegerChoices):
    first = 1, "1st"
    second = 2, "2nd"
    third = 3, "3rd"
    fourth = 4, "4th"
    fifth = 5, "5th"
    sixth = 6, "6th"
    seventh = 7, "7th"
    eighth = 8, "8th"
    ninth = 9, "9th"
    tenth = 10, "10th"
    eleventh = 11, "11th"
    twelfth = 12, "12th"


class Weekday(IntegerChoices):
    monday = 0, "Mon"
    tuesday = 1, "Tues"
    wednesday = 2, "Wed"
    thursday = 3, "Thurs"
    friday = 4, "Friday"
    saturday = 5, "Sat"
    sunday = 6, "Sun"


class USStateEquiv(TextChoices):
    AK = "AK", "Alaska"
    AL = "AL", "Alabama"
    AR = "AR", "Arkansas"
    AS = "AS", "American Samoa"
    AZ = "AZ", "Arizona"
    CA = "CA", "California"
    CO = "CO", "Colorado"
    CT = "CT", "Connecticut"
    DC = "DC", "Washington D.C."
    DE = "DE", "Delaware"
    FL = "FL", "Florida"
    FM = "FM", "Federated States Of Micronesia"
    GA = "GA", "Georgia"
    GU = "GU", "Guam"
    HI = "HI", "Hawaii"
    IA = "IA", "Iowa"
    ID = "ID", "Idaho"
    IL = "IL", "Illinois"
    IN = "IN", "Indiana"
    KS = "KS", "Kansas"
    KY = "KY", "Kentucky"
    LA = "LA", "Louisiana"
    MA = "MA", "Massachusetts"
    MD = "MD", "Maryland"
    ME = "ME", "Maine"
    MH = "MH", "Marshall Islands"
    MI = "MI", "Michigan"
    MN = "MN", "Minnesota"
    MO = "MO", "Missouri"
    MP = "MP", "Northern Mariana Islands"
    MS = "MS", "Mississippi"
    MT = "MT", "Montana"
    NC = "NC", "North Carolina"
    ND = "ND", "North Dakota"
    NE = "NE", "Nebraska"
    NH = "NH", "New Hampshire"
    NJ = "NJ", "New Jersey"
    NM = "NM", "New Mexico"
    NV = "NV", "Nevada"
    NY = "NY", "New York"
    OH = "OH", "Ohio"
    OK = "OK", "Oklahoma"
    OR = "OR", "Oregon"
    PA = "PA", "Pennsylvania"
    PR = "PR", "Puerto Rico"
    PW = "PW", "Palau"
    RI = "RI", "Rhode Island"
    SC = "SC", "South Carolina"
    SD = "SD", "South Dakota"
    TN = "TN", "Tennessee"
    TX = "TX", "Texas"
    UT = "UT", "Utah"
    VA = "VA", "Virginia"
    VI = "VI", "U.S. Virgin Islands"
    VT = "VT", "Vermont"
    WA = "WA", "Washington"
    WI = "WI", "Wisconsin"
    WV = "WV", "West Virginia"
    WY = "WY", "Wyoming"


class ShirtSize(TextChoices):
    XXS = "XXS", "XXS"
    XS = "XS", "XS"
    S = "S",
    M = "M"
    L = "L"
    XL = "XL", "XL"
    XXL = "XXL", "XXL"
