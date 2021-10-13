from django.db.models import IntegerChoices, TextChoices


class UserType(TextChoices):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    guardian = "guardian"
    onsite_volunteer = "onsite_volunteer", "On-site Volunteer"


class PermissionType(TextChoices):
    # WIP: permissions list TBD
    view_courses = "view_courses"
    edit_courses = "edit_courses"
    view_all_programs = "view_all_programs"
    edit_programs = "edit_programs"
    view_student_dashboard = "view_student_dashboard"
    view_all_student_dashboards = "view_all_student_dashboards"
    view_teacher_dashboard = "view_teacher_dashboard"
    view_all_teacher_dashboards = "view_all_teacher_dashboards"


class GradeLevel(IntegerChoices):
    first = 1, '1st'
    second = 2, '2nd'
    third = 3, '3rd'
    fourth = 4, '4th'
    fifth = 5, '5th'
    sixth = 6, '6th'
    seventh = 7, '7th'
    eighth = 8, '8th'
    ninth = 9, '9th'
    tenth = 10, '10th'
    eleventh = 11, '11th'
    twelfth = 12, '12th'


class Weekday(IntegerChoices):
    monday = 0, "Mon"
    tuesday = 1, "Tues"
    wednesday = 2, "Wed"
    thursday = 3, "Thurs"
    friday = 4, "Friday"
    saturday = 5, "Sat"
    sunday = 6, "Sun"


class USState(TextChoices):
    AL = 'AL', 'Alabama'
    AK = 'AK', 'Alaska'
    AZ = 'AZ', 'Arizona'
    AR = 'AR', 'Arkansas'
    CA = 'CA', 'California'
    CO = 'CO', 'Colorado'
    CT = 'CT', 'Connecticut'
    DC = 'DC', 'Washington D.C.'
    DE = 'DE', 'Delaware'
    FL = 'FL', 'Florida'
    GA = 'GA', 'Georgia'
    HI = 'HI', 'Hawaii'
    ID = 'ID', 'Idaho'
    IL = 'IL', 'Illinois'
    IN = 'IN', 'Indiana'
    IA = 'IA', 'Iowa'
    KS = 'KS', 'Kansas'
    KY = 'KY', 'Kentucky'
    LA = 'LA', 'Louisiana'
    ME = 'ME', 'Maine'
    MD = 'MD', 'Maryland'
    MA = 'MA', 'Massachusetts'
    MI = 'MI', 'Michigan'
    MN = 'MN', 'Minnesota'
    MS = 'MS', 'Mississippi'
    MO = 'MO', 'Missouri'
    MT = 'MT', 'Montana'
    NE = 'NE', 'Nebraska'
    NV = 'NV', 'Nevada'
    NH = 'NH', 'New Hampshire'
    NJ = 'NJ', 'New Jersey'
    NM = 'NM', 'New Mexico'
    NY = 'NY', 'New York'
    NC = 'NC', 'North Carolina'
    ND = 'ND', 'North Dakota'
    OH = 'OH', 'Ohio'
    OK = 'OK', 'Oklahoma'
    OR = 'OR', 'Oregon'
    PA = 'PA', 'Pennsylvania'
    RI = 'RI', 'Rhode Island'
    SC = 'SC', 'South Carolina'
    SD = 'SD', 'South Dakota'
    TN = 'TN', 'Tennessee'
    TX = 'TX', 'Texas'
    UT = 'UT', 'Utah'
    VT = 'VT', 'Vermont'
    VA = 'VA', 'Virginia'
    WA = 'WA', 'Washington'
    WI = 'WI', 'Wisconsin'
    WV = 'WV', 'West Virginia'
    WY = 'WY', 'Wyoming'
