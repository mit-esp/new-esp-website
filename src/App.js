import {useEffect, useMemo, useState} from "react";
import {Form} from 'react-bootstrap';
import dayjs from "dayjs";


const DAYS_OF_WEEK = ['Mondays', 'Tuesdays', 'Wednesdays', 'Thursdays', 'Fridays', 'Saturdays', 'Sundays']
const DEFAULT_FILTERS = {
  hideUnavailableTimeSlots: true,
  hideFullyScheduledCourses: true,
  ...Object.fromEntries(DAYS_OF_WEEK.map((dayOfWeek) => [`show${dayOfWeek}`, true]))
}


export default function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [courses, setCourses] = useState([])
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [selectedCourseId, setSelectedCourseId] = useState(null)
  const [timeSlots, setTimeSlots] = useState([])

  useEffect(() => {
    loadData('/api/v0/courses', setCourses)
    loadData('/api/v0/classrooms', setClassrooms)
    loadData(
      '/api/v0/time-slots',
      setTimeSlots,
      (timeSlot) => ({
        ...timeSlot,
        // TODO: This converts to local time; is this appropriate?
        end_datetime: dayjs(timeSlot.end_datetime),
        start_datetime: dayjs(timeSlot.start_datetime),
      })
    )
    loadData('/api/v0/classroom-time-slots', setClassroomTimeSlots)

    async function loadData(endpoint, setStateFunc, processFunc) {
      const response = await fetch(`http://localhost:8000${endpoint}`)
      let data = (await response.json()).data
      if (processFunc !== undefined) {
        data = data.map((datum) => processFunc(datum))
      }
      setStateFunc(data)
    }
  }, [])

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

  return (
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
                    <button
                      className={`btn btn-${course.id === selectedCourseId ? 'primary' : 'light'} ${shouldShowCourse(course) ? '' : 'd-none'}`}
                      key={course.id}
                      onClick={() => selectCourse(course.id)}
                    >
                      {course.name} ({getScheduledSectionsCount(course)}/{course.sections_count})
                    </button>
                  ))
                  : <span>Loading...</span>
                }
              </div>
            </div>
          </div>
        </div>
        <div className={`calendar ${selectedCourseId === null ? '' : 'course-selected'}`}>
          <div className='card'>
            {classroomTimeSlots.length || classrooms.length || timeSlots.length
              ? (
                <div className='table-responsive'>
                  <table className='table'>
                    <thead>
                      <tr>
                        <th className='sticky column header' scope='col' />
                        {classrooms.map((classroom) => (
                          <th className='sticky header' key={classroom.id} scope='col'>{classroom.name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {timeSlots.map((timeSlot) => (
                        <tr className={shouldShowTimeSlot(timeSlot) ? '' : 'd-none'} key={timeSlot.id}>
                          <td
                            className='sticky column'
                            dangerouslySetInnerHTML={{__html: timeSlotDisplayHtml(timeSlot)}}
                          />
                          {classrooms.map((classroom) => {
                            const classroomTimeSlot = getClassroomTimeSlot(timeSlot.id, classroom.id)
                            return (
                              <td className={getClassroomTimeSlotClassNames(classroomTimeSlot)}>
                                {classroomTimeSlot.course_name}
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                // <Table columns={columns} data={data} />
              )
              : <div>Loading...</div>
            }
          </div>
        </div>
        <div className='options'>
          <div className='card actions'>
            <div className='card-body'>
              <h5 className='card-title'>Actions</h5>
            </div>
          </div>
          <div className='card filters'>
            <div className='card-body'>
              <h5 className='card-title'>Filters</h5>
              <h6>Schedule</h6>
              <hr />
              <Form.Check
                checked={filters.hideUnavailableTimeSlots}
                label='Hide unavailable time slots'
                onChange={() => toggleFilter('hideUnavailableTimeSlots')}
                type='checkbox'
              />
              <small>Days of week</small>
              {DAYS_OF_WEEK.map((dayOfWeek) => (
                <Form.Check
                  checked={filters[`show${dayOfWeek}`]}
                  label={`Show ${dayOfWeek}`}
                  onChange={() => toggleFilter(`show${dayOfWeek}`)}
                  type='checkbox'
                />
              ))}
              <br />
              <h6>Courses</h6>
              <hr />
              <Form.Check
                checked={filters.hideFullyScheduledCourses}
                label='Hide fully scheduled courses'
                onChange={() => toggleFilter('hideFullyScheduledCourses')}
                type='checkbox'
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

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

  function getClassroomTimeSlotClassNames(classroomTimeSlot) {
    const classNames = []

    // Availability
    classNames.push('availability')
    if (classroomTimeSlot.id === undefined) {
      classNames.push('unavailable')
    } else if (!classroomTimeSlot.course_section_id) {
      classNames.push('available')
    } else {
      classNames.push('scheduled')
    }

    // Is selected course
    if (classroomTimeSlot.course_id === selectedCourseId) {
      classNames.push('selected-course')
    }

    return classNames.join(' ')
  }

  function getScheduledSectionsCount(course) {
    return classroomTimeSlots.filter((classroomTimeSlot) => (
      classroomTimeSlot.course_id === course.id
    )).length
  }

  function selectCourse(courseId) {
    if (selectedCourseId === courseId) {
      setSelectedCourseId(null)
    } else {
      setSelectedCourseId(courseId)
    }
  }

  function shouldShowCourse(course) {
    if (filters.hideFullyScheduledCourses) {
      // Hide fully scheduled courses
      if (course.sections_count === getScheduledSectionsCount(course)) {
        return false
      }
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
    return true
  }

  function timeSlotDisplayHtml(timeSlot) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}<br>${startTimeDisplay} - ${endTimeDisplay}`
  }

  function toggleFilter(filterName) {
    setFilters({...filters, [filterName]: !filters[filterName]})
  }
}
