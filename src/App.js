import {useEffect, useMemo, useState} from "react";
import dayjs from "dayjs";
import {useTable} from "react-table";

export default function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [courses, setCourses] = useState([])
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
    classroomTimeSlots.reduce((acc, cts) => (
      {...acc, [cts.time_slot_id]: {...acc[cts.time_slot_id], [cts.classroom_id]: cts}}
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
                      className={`btn btn-${course.id === selectedCourseId ? 'primary' : 'light'}`}
                      key={course.id}
                      onClick={() => selectCourse(course.id)}
                    >
                      {course.name}
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
                        <th className='sticky column header' scope='col'></th>
                        {classrooms.map((classroom) => (
                          <th className='sticky header' key={classroom.id} scope='col'>{classroom.name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {timeSlots.map((timeSlot) => (
                        <tr key={timeSlot.id}>
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

  function selectCourse(courseId) {
    if (selectedCourseId === courseId) {
      setSelectedCourseId(null)
    } else {
      setSelectedCourseId(courseId)
    }
  }

  function timeSlotDisplayHtml(timeSlot) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}<br>${startTimeDisplay} - ${endTimeDisplay}`
  }
}
