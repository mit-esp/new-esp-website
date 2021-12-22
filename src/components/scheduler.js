import {useMemo} from "react";
import {DAYS_OF_WEEK} from "../constants";
import {LoadingSpinner} from "./loadingSpinner";

export function Scheduler(props) {
  const {
    classrooms,
    classroomTimeSlots,
    filters,
    loading,
    selected,
    setSelected,
    timeSlots,
  } = props

  /**
   * Create a lookup table for classroomTimeSlot first by timeSlot.id, then by classroom.id
   */
  const classroomTimeSlotLookupTable = useMemo(() => (
    classroomTimeSlots.reduce((accumulator, classroomTimeSlot) => (
      {
        ...accumulator,
        [classroomTimeSlot.time_slot_id]: {
          ...accumulator[classroomTimeSlot.time_slot_id],
          [classroomTimeSlot.classroom_id]: classroomTimeSlot,
        },
      }
    ), {})
  ), [classroomTimeSlots])
  const selectedAssignedClassroomTimeSlotIds = (
    Object
      .entries(selected.assignments)
      .filter(([_, courseSectionId]) => courseSectionId !== null)
      .map(([classroomTimeSlotId, _]) => classroomTimeSlotId)
  )

  return (
    <div className='card'>
      {loading
        ? <LoadingSpinner centered={true} />
        : classroomTimeSlots.length === 0 || classrooms.length === 0 || timeSlots.length === 0
          ? <p>(No available classroom time slots)</p>
          : (
            <div className='table-responsive'>
              <table className='table'>
                <thead>
                <tr>
                  <th className='sticky column header' scope='col' />
                  {classrooms.map((classroom) => (
                    <th
                      className={getClassroomClassNames(classroom, true)}
                      key={classroom.id}
                      scope='col'
                    >
                      {classroom.name}
                    </th>
                  ))}
                </tr>
                </thead>
                <tbody>
                {timeSlots.map((timeSlot) => (
                  <tr className={shouldShowTimeSlot(timeSlot) ? '' : 'd-none'} key={timeSlot.id}>
                    <td
                      className='sticky column'
                      dangerouslySetInnerHTML={{__html: timeSlotDisplay(timeSlot, true)}}
                    />
                    {classrooms.map((classroom) => {
                      const classroomTimeSlot = getClassroomTimeSlot(timeSlot.id, classroom.id)
                      return (
                        <td
                          className={getClassroomTimeSlotClassNames(classroomTimeSlot, classroom)}
                          key={`${timeSlot.id}-${classroom.id}`}
                          onClick={
                            isClickable(classroomTimeSlot)
                              ? () => selectClassroomTimeSlot(classroomTimeSlot)
                              : null
                          }
                        >
                          {getClassroomTimeSlotDisplay(classroomTimeSlot)}
                        </td>
                      )
                    })}
                  </tr>
                ))}
                </tbody>
              </table>
            </div>
          )
      }
    </div>
  )

  function getClassroomClassNames(classroom, header=false) {
    const classNames = []

    // Sticky headers
    if (header) {
      classNames.push('sticky')
      classNames.push('header')
    }

    // Classroom search filter
    if (filters.classroomName !== '') {
      if (!classroom.name.toLowerCase().includes(filters.classroomName.toLowerCase())) {
        classNames.push('d-none')
      }
    }

    return classNames.join(' ')
  }

  function getClassroomTimeSlot(timeSlotId, classroomId) {
    let selector
    selector = classroomTimeSlotLookupTable[timeSlotId]
    if (selector === undefined) {
      return {}
    }
    selector = selector[classroomId]
    if (selector === undefined) {
      return {}
    }
    return selector
  }

  function getClassroomTimeSlotDisplay(classroomTimeSlot) {
    if (!selected.course) {
      return classroomTimeSlot.course_name
    }
    if (isDescheduled(classroomTimeSlot)) {
      return 'unscheduled'
    }
    if (!Object.keys(selected.assignments).includes(classroomTimeSlot.id)) {
      return ''
    }
    return `Section ${selected.assignments[classroomTimeSlot.id]?.display_id}`
  }

  function getClassroomTimeSlotClassNames(classroomTimeSlot, classroom) {
    const classNames = []

    // Classroom filters
    classNames.push(getClassroomClassNames(classroom))

    // Availability
    classNames.push('availability')
    if (classroomTimeSlot.id === undefined) {
      classNames.push('unavailable')
      // If it's unavailable, it shouldn't have any other classes
      return classNames.join(' ')
    } else if (!classroomTimeSlot.course_section_id) {
      classNames.push('available')
    } else {
      classNames.push('scheduled')
    }

    // Is selected course
    if (classroomTimeSlot.course_id === selected.course?.id) {
      classNames.push('selected-course')
    }

    // Is selected course section
    if (
      selected.courseSection !== null
      && selected.assignments[classroomTimeSlot.id]?.id === selected.courseSection.id
    ) {
      classNames.push('selected-course-section')
    }

    // Interactivity
    if (isClickable(classroomTimeSlot)) {
      classNames.push('clickable')
    }
    if (isSelected(classroomTimeSlot)) {
      classNames.push('selected')
    }
    if (isDescheduled(classroomTimeSlot)) {
      classNames.push('descheduled')
    }

    return classNames.join(' ')
  }

  function isClickable(classroomTimeSlot) {
    // No available ClassroomTimeSlot means it's not available for scheduling
    if (classroomTimeSlot?.id === undefined) return false

    // Not in selection context
    if (selected.course === null) return false
    if (selected.courseSection === null) return false

    if (classroomTimeSlot?.course_section_id === null) {
      // ClassroomTimeSlot is not yet taken, so it's clickable as long as no other section has it selected or if it's
      // selected for this section
      return (
        selected.assignments[classroomTimeSlot.id] === undefined
        || selected.courseSection.id === selected.assignments[classroomTimeSlot.id]?.id
      )
    } else {
      /// ClassroomTimeSlot is taken, so it's only clickable if it's taken by this section
      return classroomTimeSlot?.course_section_id === selected.courseSection.id
    }
  }

  function isDescheduled(classroomTimeSlot) {
    return selected.assignments[classroomTimeSlot?.id] === null
  }

  function isSelected(classroomTimeSlot) {
    return (
      selectedAssignedClassroomTimeSlotIds.includes(classroomTimeSlot?.id)
      || (
        (classroomTimeSlot?.course_section_id ?? null) !== null
        && classroomTimeSlot?.course_section_id === selected.courseSection?.id
        && selected.assignments[classroomTimeSlot?.id] !== null
      )
    )
  }

  function selectClassroomTimeSlot(classroomTimeSlot) {
    const newAssignments = {...selected.assignments}
    if (classroomTimeSlot.course_section_id === selected.courseSection.id) {
      if (selected.assignments[classroomTimeSlot.id] === null) {
        // Deleting since it is an already saved assignment
        newAssignments[classroomTimeSlot.id] = selected.courseSection
      } else {
        // Marking as null since we're unassigning a saved assignment
        newAssignments[classroomTimeSlot.id] = null
      }
    } else {
      if (selectedAssignedClassroomTimeSlotIds.includes(classroomTimeSlot.id)) {
        // We're deselecting
        delete newAssignments[classroomTimeSlot.id]
      } else {
        newAssignments[classroomTimeSlot.id] = selected.courseSection
      }
    }
    setSelected({...selected, assignments: newAssignments})
  }

  function shouldShowTimeSlot(timeSlot) {
    // Hide unavailable time slots
    if (filters.hideUnavailableTimeSlots) {
      const classroomLookup = classroomTimeSlotLookupTable[timeSlot.id]
      if (classroomLookup === undefined) {
        return false
      }
      if (Object.values(classroomLookup).map((classroomTimeSlot) => !classroomTimeSlot.course_section_id).every((x) => !x)) {
        return false
      }
    }
    // Hide days of week
    for (const dayOfWeek of DAYS_OF_WEEK) {
      const filterName = `show${dayOfWeek}`
      if (!filters[filterName]) {
        if (dayOfWeek.startsWith(timeSlot.start_datetime.format('dddd'))) {
          return false
        }
      }
    }
    // Show only after date
    if (filters.dateStart) {
      if (timeSlot.start_datetime.isBefore(filters.dateStart)) {
        return false
      }
    }
    // Show only after time
    if (filters.timeStart) {
      const [hour, minute] = filters.timeStart.split(':').map((text) => parseInt(text, 10))
      if (
        timeSlot.start_datetime.hour() < hour
        || (timeSlot.start_datetime.hour() === hour && timeSlot.start_datetime.minute() < minute)
      ) {
        return false
      }
    }
    // Show only before date
    if (filters.dateEnd) {
      if (timeSlot.start_datetime.isSame(filters.dateEnd) || timeSlot.start_datetime.isAfter(filters.dateEnd)) {
        return false
      }
    }
    // Show only before time
    if (filters.timeEnd) {
      const [hour, minute] = filters.timeEnd.split(':').map((text) => parseInt(text, 10))
      if (
        timeSlot.start_datetime.hour() > hour
        || (timeSlot.start_datetime.hour() === hour && timeSlot.start_datetime.minute() >= minute)
      ) {
        return false
      }
    }

    // Show only if teachers are available
    if (filters.teachersAvailable && selected.course !== null) {
      if (!Object.keys(timeSlot.course_teacher_availabilities).includes(selected.course.id)) {
        return false
      }
    }

    return true
  }

  function timeSlotDisplay(timeSlot, html=false) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}${html ? '<br>' : ' '}${startTimeDisplay} - ${endTimeDisplay}`
  }
}
