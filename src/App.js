import {useEffect, useMemo, useState} from "react";
import {Modal, Toast} from 'react-bootstrap';
import dayjs from "dayjs";
import {getQueryParam, loadData, secureFetch, useStateWithCallback} from "./utils";
import {BsExclamationCircleFill, BsFillCheckCircleFill, BsInfoCircleFill} from "react-icons/all";
import {CheckboxFilter, TextFilter} from "./filters";


const DAYS_OF_WEEK = ['Mondays', 'Tuesdays', 'Wednesdays', 'Thursdays', 'Fridays', 'Saturdays', 'Sundays']
const DEFAULT_FILTERS = {
  classroomName: '',
  courseName: '',
  dateEnd: '',
  dateStart: '',
  hideUnavailableTimeSlots: false,
  hideFullyScheduledCourses: false,
  teachersAvailable: true,
  timeEnd: '',
  timeStart: '',
  ...Object.fromEntries(DAYS_OF_WEEK.map((dayOfWeek) => [`show${dayOfWeek}`, true])),
}
const DEFAULT_SELECTED = {
  assignments: {},  // classroomTimeSlotId<string>:courseSection<object>
  course: null,
  courseSection: null,
}
const TOAST_TYPES = {
  secondary: 'secondary',
  success: 'success',
  warning: 'warning',
}
const DEFAULT_TOAST_OPTIONS = {
  message: '',
  show: false,
  type: TOAST_TYPES.success,
}


export default function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [courses, setCourses] = useState([])
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [selected, setSelected] = useState(DEFAULT_SELECTED)
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toastOptions, setToastOptions] = useStateWithCallback(DEFAULT_TOAST_OPTIONS)
  const [timeSlots, setTimeSlots] = useState([])

  const programId = useMemo(() => getQueryParam('program_id'), [])

  const classroomById = useMemo(() => (
    classrooms.reduce((accumulator, classroom) => ({...accumulator, [classroom.id]: classroom}), {})
  ), [classrooms])

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

  const classroomTimeSlotsToSubmit = classroomTimeSlots.filter((classroomTimeSlot) => {
    if (!Object.keys(selected.assignments).includes(classroomTimeSlot.id)) {
      return false
    }
    if (selected.assignments[classroomTimeSlot.id]?.id === classroomTimeSlot.course_section_id) {
      return false
    }
    return true
  })
  const selectedAssignedClassroomTimeSlotIds = (
    Object
      .entries(selected.assignments)
      .filter(([_, courseSectionId]) => courseSectionId !== null)
      .map(([classroomTimeSlotId, _]) => classroomTimeSlotId)
  )

  useEffect(() => {
    loadData('/api/v0/classrooms/', setClassrooms)
    loadData(
      `/api/v0/programs/${programId}/classroom-time-slots/`,
      setClassroomTimeSlots,
      processTimeSlots,
    )
    loadData(`/api/v0/programs/${programId}/courses/`, setCourses)
    loadData(
      `/api/v0/programs/${programId}/time-slots/`,
      setTimeSlots,
      processTimeSlots,
    )
  }, [programId])

  return programId === undefined ? (
    <p>No program specified. Please add `?program_id=&lt;program_id&gt;` to the url.</p>
  ) : (
    <div className='scheduler'>
      <h1>Scheduler</h1>
      <div className='interface-wrapper'>
        <div className='courses'>
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
        </div>
        <div className={`calendar ${selected.course === null ? '' : 'course-selected'}`}>
          <div className='card'>
            {classroomTimeSlots.length || classrooms.length || timeSlots.length
              ? (
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
              : <div>(No Time Slots)</div>
            }
          </div>
        </div>
        <div className='options'>
          <div className='card actions'>
            <div className='card-body'>
              <h5 className='card-title'>Actions</h5>
              <dl className='mb-0'>
                <dt>Course</dt>
                <dd>{selected.course === null ? '--' : selected.course?.name}</dd>
                <dt>Course Section</dt>
                <dd>
                  {selected.courseSection === null ? '--' : `Section ${selected.courseSection?.display_id}`}
                </dd>
              </dl>
              <div className='d-grid gap-2'>
                <button
                  className={`btn btn-${classroomTimeSlotsToSubmit.length === 0 ? 'light' : 'success'}`}
                  disabled={classroomTimeSlotsToSubmit.length === 0}
                  onClick={() => setShowSubmitModal(true)}
                >
                  Preview changes
                </button>
                <button
                  className='btn btn-link'
                  disabled={selected.course === null}
                  onClick={() => setSelected(DEFAULT_SELECTED)}
                >
                  Clear selections
                </button>
              </div>
            </div>
          </div>
          <div className='card filters'>
            <div className='card-body'>
              <h5 className='card-title'>Filters</h5>
              <div className='filters-list'>
                <h6>Schedule</h6>
                <hr />
                <CheckboxFilter
                  filters={filters}
                  filterKey='hideUnavailableTimeSlots'
                  filterLabel='Hide unavailable time slots'
                  setFilters={setFilters}
                />
                <CheckboxFilter
                  filters={filters}
                  filterKey='teachersAvailable'
                  filterLabel='Show only time slots with teacher availability'
                  setFilters={setFilters}
                />
                <TextFilter
                  filters={filters}
                  filterKey='dateStart'
                  filterLabel='Show only on or after date'
                  inputProps={{pattern: '[0-9]{4}-[0-9]{2}-[0-9]{2}', type: 'date'}}
                  setFilters={setFilters}
                />
                <TextFilter
                  filters={filters}
                  filterKey='timeStart'
                  filterLabel='Show only on or after time'
                  inputProps={{pattern: '[0-9]{2}:[0-9]{2}', type: 'time'}}
                  setFilters={setFilters}
                />
                <TextFilter
                  filters={filters}
                  filterKey='dateEnd'
                  filterLabel='Show only before date'
                  inputProps={{pattern: '[0-9]{4}-[0-9]{2}-[0-9]{2}', type: 'date'}}
                  setFilters={setFilters}
                />
                <TextFilter
                  filters={filters}
                  filterKey='timeEnd'
                  filterLabel='Show only before time'
                  inputProps={{pattern: '[0-9]{2}:[0-9]{2}', type: 'time'}}
                  setFilters={setFilters}
                />
                <small>Days of week</small>
                {DAYS_OF_WEEK.map((dayOfWeek) => (
                  <CheckboxFilter
                    filters={filters}
                    filterKey={`show${dayOfWeek}`}
                    filterLabel={`Show ${dayOfWeek}`}
                    key={dayOfWeek}
                    setFilters={setFilters}
                  />
                ))}
                <br />
                <h6>Courses</h6>
                <hr />
                <CheckboxFilter
                  filters={filters}
                  filterKey='hideFullyScheduledCourses'
                  filterLabel='Hide fully scheduled course'
                  setFilters={setFilters}
                />
                <TextFilter
                  filters={filters}
                  filterKey='courseName'
                  filterLabel='Filter by course name'
                  inputProps={{placeholder: 'Enter course name'}}
                  setFilters={setFilters}
                />
                <br />
                <h6>Classrooms</h6>
                <hr />
                <TextFilter
                  filters={filters}
                  filterKey='classroomName'
                  filterLabel='Filter by classroom name'
                  inputProps={{placeholder: 'Enter classroom name'}}
                  setFilters={setFilters}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <Modal onHide={() => setShowSubmitModal(false)} show={showSubmitModal}>
        <Modal.Header closeButton>
          <Modal.Title>Changes</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Please review the following changes before submitting.</p>
          <dl>
            <dt>Course</dt>
            <dd>{selected.course?.name}</dd>
          </dl>
          <ul>
            {showSubmitModal && displayChangesPreview()}
          </ul>
        </Modal.Body>
        <Modal.Footer>
          <button className='btn btn-link' onClick={() => setShowSubmitModal(false)}>
            Cancel
          </button>
          <button className='btn btn-success' disabled={submitting} onClick={submitting ? null : submitData}>
            Submit{submitting ? 'ting' : ''}
          </button>
        </Modal.Footer>
      </Modal>
      <Toast
        autohide
        bg={toastOptions.type}
        delay={8000}
        onClose={() => setToastOptions({...toastOptions, show: false})}
        show={toastOptions.show}
      >
        <Toast.Header>
          <div className={`text-${toastOptions.type} me-auto`}>
            <span hidden={toastOptions.type !== TOAST_TYPES.success}>
              <BsFillCheckCircleFill /> Success!
            </span>
            <span hidden={toastOptions.type !== TOAST_TYPES.warning}>
              <BsExclamationCircleFill /> Warning!
            </span>
            <span hidden={toastOptions.type !== TOAST_TYPES.secondary}>
              <BsInfoCircleFill /> Scheduler
            </span>
          </div>
        </Toast.Header>
        <Toast.Body>{toastOptions.message}</Toast.Body>
      </Toast>
    </div>
  )

  function displayChangesPreview() {
    const sortedSelectedClassroomTimeSlots = classroomTimeSlotsToSubmit.sort((a, b) => {
      if (a.classroom_id === b.classroom_id) {
        return a.start_datetime > b.start_datetime ? 1 : -1
      }
      return a.classroom_id > b.classroom_id ? 1 : -1
    })
    const timeRangeDisplays = []
    let currentClassroom = null
    let currentEnd = null
    let currentStart = null
    let previousUnscheduling = null;
    for (const selectedClassroomTimeSlot of sortedSelectedClassroomTimeSlots) {
      const differentClassroom = currentClassroom === null || currentClassroom.id !== selectedClassroomTimeSlot.classroom_id
      if (differentClassroom || currentStart === null ) {
        currentClassroom = classroomById[selectedClassroomTimeSlot.classroom_id]
        currentStart = selectedClassroomTimeSlot.start_datetime
      }
      const isUnscheduling = selected.assignments[selectedClassroomTimeSlot.id] === null
      const continuation = (
        previousUnscheduling === isUnscheduling
        && currentEnd !== null
        && currentEnd.isSame(selectedClassroomTimeSlot.start_datetime)
      )
      if (continuation) {
        timeRangeDisplays.pop()
      } else {
        currentStart = selectedClassroomTimeSlot.start_datetime
      }
      currentEnd = selectedClassroomTimeSlot.end_datetime
      const startTimeFormat = 'M/D h:mma'
      const endTimeFormat = currentStart.date() === currentEnd.date() ? 'h:mma' : startTimeFormat
      timeRangeDisplays.push(
        <li key={selectedClassroomTimeSlot.id}>
          <ul className='list-unstyled'>
            <li>
              {isUnscheduling ? 'Unscheduling' : 'Scheduling' }{' '}
              Section{' '}
              {(selected.assignments[selectedClassroomTimeSlot.id] ?? selectedClassroomTimeSlot.course_section).display_id}
            </li>
            <li>
              {currentStart.format(startTimeFormat)} - {currentEnd.format(endTimeFormat)}{' '}
              ({currentEnd.diff(currentStart, 'minute', true)} minutes)
            </li>
            <li>Classroom "{currentClassroom.name}"</li>
          </ul>
        </li>
      )
      previousUnscheduling = isUnscheduling
    }
    return timeRangeDisplays
  }

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

  function processTimeSlots(classroomTimeSlots) {
    return classroomTimeSlots.map((classroomTimeSlot) => ({
      ...classroomTimeSlot,
      // TODO: This converts to local time; is this appropriate?
      end_datetime: dayjs(classroomTimeSlot.end_datetime),
      start_datetime: dayjs(classroomTimeSlot.start_datetime),
    }))
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

  function showToast(message, type=TOAST_TYPES.secondary) {
    if (toastOptions.show === true) {
      setToastOptions({...toastOptions, show: false}, () => _showToast(message, type))
    } else {
      _showToast(message, type)
    }

    function _showToast(message, type) {
      setToastOptions({message, show: true, type})
    }
  }

  async function submitData() {
    setSubmitting(true)
    const data = Object.entries(selected.assignments).map(([classroomTimeSlotId, courseSection]) => ({
      classroom_time_slot_id: classroomTimeSlotId,
      course_section_id: courseSection?.id ?? null,
    }))

    let response
    try {
      response = await secureFetch(
        `${process.env.REACT_APP_API_BASE_URL}/api/v0/programs/${programId}/assign-classroom-time-slots/`,
        {
          body: JSON.stringify({data}),
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          method: 'POST',
        }
      )
    } catch (e) {
      return showToast('Oops! There was an issue communicating with the server.', TOAST_TYPES.warning)
    }

    if (!response.ok) {
      return showToast('Oops! Something went wrong with submitting your data.', TOAST_TYPES.warning)
    }

    await loadData(
      `/api/v0/programs/${programId}/classroom-time-slots/`,
      setClassroomTimeSlots,
      _processTimeSlots,
    )
    showToast('Your changes have been saved!', TOAST_TYPES.success)

    function _processTimeSlots(data) {
      setSelected(DEFAULT_SELECTED)
      setShowSubmitModal(false)
      setSubmitting(false)
      return processTimeSlots(data)
    }
  }

  function timeSlotDisplay(timeSlot, html=false) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}${html ? '<br>' : ' '}${startTimeDisplay} - ${endTimeDisplay}`
  }
}
