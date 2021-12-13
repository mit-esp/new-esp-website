import {useEffect, useMemo, useState} from "react";
import dayjs from "dayjs";
import {getQueryParam, loadData} from "./utils";
import {CourseSelector} from "./components/course-selector";
import {Scheduler} from "./components/scheduler";
import {DAYS_OF_WEEK} from "./constants";
import {Filters} from "./components/filters";
import {Actions} from "./components/actions";


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

export default function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [courses, setCourses] = useState([])
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [selected, setSelected] = useState(DEFAULT_SELECTED)
  const [timeSlots, setTimeSlots] = useState([])

  const programId = useMemo(() => getQueryParam('program_id'), [])

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
          <CourseSelector
            classroomTimeSlots={classroomTimeSlots}
            courses={courses}
            filters={filters}
            selected={selected}
            setSelected={setSelected}
            DEFAULT_SELECTED={DEFAULT_SELECTED}
          />
        </div>
        <div className={`calendar ${selected.course === null ? '' : 'course-selected'}`}>
          <Scheduler
            classrooms={classrooms}
            classroomTimeSlots={classroomTimeSlots}
            filters={filters}
            selected={selected}
            setSelected={setSelected}
            timeSlots={timeSlots}
          />
        </div>
        <div className='options'>
          <Actions
            classrooms={classrooms}
            classroomTimeSlots={classroomTimeSlots}
            processTimeSlots={processTimeSlots}
            programId={programId}
            selected={selected}
            setClassroomTimeSlots={setClassroomTimeSlots}
            setSelected={setSelected}
            DEFAULT_SELECTED={DEFAULT_SELECTED}
          />
          <Filters
            filters={filters}
            setFilters={setFilters}
          />
        </div>
      </div>
    </div>
  )

  function processTimeSlots(classroomTimeSlots) {
    return classroomTimeSlots.map((classroomTimeSlot) => ({
      ...classroomTimeSlot,
      // TODO: This converts to local time; is this appropriate?
      end_datetime: dayjs(classroomTimeSlot.end_datetime),
      start_datetime: dayjs(classroomTimeSlot.start_datetime),
    }))
  }
}
