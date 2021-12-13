export function CourseSelector(props) {
  const {
    classroomTimeSlots,
    courses,
    filters,
    selected,
    setSelected,
    DEFAULT_SELECTED,
  } = props

  return (
    <div className='card'>
      <div className='card-body'>
        <h5 className='card-title'>Courses</h5>
        <p className='card-subtitle mb-2 text-muted'>Please select a course</p>
        <div className='course-list d-grid'>
          {courses.length
            ? courses.map((course) => (
              <div
                className={getCourseClassNames(course)}
                key={course.id}
                onClick={() => selectCourse(course)}
              >
                <span>{course.name} ({getScheduledSectionsCount(course)}/{course.sections_count})</span>
                <div className={`d-grid mt-2 ${course.id === selected.course?.id ? '' : 'd-none'}`}>
                  {course.sections.map((section) => (
                    <div
                      className={getCourseSectionClassNames(section)}
                      key={section.id}
                      onClick={(event) => selectCourseSection(section, event)}
                    >
                      Section {section.display_id}
                    </div>
                  ))}
                </div>
              </div>
            ))
            : <span>(No Courses)</span>
          }
        </div>
      </div>
    </div>
  )

  function getCourseClassNames(course) {
    const classNames = []
    const isSelectedCourse = course.id === selected.course?.id

    // General styling
    classNames.push('btn')
    classNames.push(`btn-${isSelectedCourse ? 'primary' : 'light'}`)
    classNames.push('mb-2')

    // Filters
    if (!shouldShowCourse(course)) {
      classNames.push('d-none')
    }

    return classNames.join(' ')
  }

  function getCourseSectionClassNames(section) {
    const classNames = []
    const isSelectedCourseSection = section.id === selected.courseSection?.id

    // General styling
    classNames.push('btn')
    classNames.push(`btn-${isSelectedCourseSection ? 'info' : 'secondary'}`)

    return classNames.join(' ')
  }

  function getScheduledSectionsCount(course) {
    return classroomTimeSlots.filter((classroomTimeSlot) => (
      classroomTimeSlot.course_id === course.id
    )).length
  }

  function selectCourse(course) {
    if (selected.course?.id === course.id) {
      setSelected(DEFAULT_SELECTED)
    } else {
      const newAssignments = {...DEFAULT_SELECTED.assignments}
      for (const classroomTimeSlot of classroomTimeSlots) {
        if (classroomTimeSlot.course_id === course.id) {
          newAssignments[classroomTimeSlot.id] = classroomTimeSlot.course_section
        }
      }
      setSelected({...selected, assignments: newAssignments, course})
    }
  }

  function selectCourseSection(courseSection, event) {
    event.stopPropagation()
    const newAssignments = {...selected.assignments}
    if (selected.courseSection?.id === courseSection.id) {
      // Also deselect any already saved assignments
      for (const classroomTimeSlot of classroomTimeSlots) {
        if (classroomTimeSlot.course_section_id === newAssignments[classroomTimeSlot.id]) {
          delete newAssignments[classroomTimeSlot.id]
        }
      }
      setSelected({...selected, assignments: newAssignments, courseSection: null})
    } else {
      // Also set already saved assignments
      for (const classroomTimeSlot of classroomTimeSlots) {
        if (classroomTimeSlot.course_section_id === courseSection.id) {
          newAssignments[classroomTimeSlot.id] = courseSection
        }
      }
      setSelected({...selected, assignments: newAssignments, courseSection})
    }
  }

  function shouldShowCourse(course) {
    if (selected.course?.id === course.id) {
      return true
    }
    if (filters.hideFullyScheduledCourses) {
      // Hide fully scheduled courses
      if (course.sections_count === getScheduledSectionsCount(course)) {
        return false
      }
    }
    if (filters.courseName !== '' && !course.name.toLowerCase().includes(filters.courseName.toLowerCase())) {
      return false
    }
    return true
  }
}
