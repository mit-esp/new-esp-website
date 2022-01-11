import {Modal, Toast} from "react-bootstrap";
import {useMemo, useState} from "react";
import {loadData, secureFetch, useStateWithCallback} from "../utils";
import {BsExclamationCircleFill, BsFillCheckCircleFill, BsInfoCircleFill} from "react-icons/all";


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

export function Actions(props) {
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [toastOptions, setToastOptions] = useStateWithCallback(DEFAULT_TOAST_OPTIONS)

  const {
    classrooms,
    classroomTimeSlots,
    processTimeSlots,
    programId,
    selected,
    setClassroomTimeSlots,
    setSelected,
    DEFAULT_SELECTED,
  } = props

  const classroomById = useMemo(() => (
    classrooms.reduce((accumulator, classroom) => ({...accumulator, [classroom.id]: classroom}), {})
  ), [classrooms])

  const classroomTimeSlotsToSubmit = classroomTimeSlots.filter((classroomTimeSlot) => {
    if (!Object.keys(selected.assignments).includes(classroomTimeSlot.id)) {
      return false
    }
    if (selected.assignments[classroomTimeSlot.id]?.id === classroomTimeSlot.course_section_id) {
      return false
    }
    return true
  })

  return (
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
      setSubmitting(false)
      return showToast('Oops! There was an issue communicating with the server.', TOAST_TYPES.warning)
    }

    if (!response.ok) {
      setSubmitting(false)
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
}
