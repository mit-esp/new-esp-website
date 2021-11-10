import './App.css';
import {useEffect, useState} from "react";
import dayjs from "dayjs";

function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [timeSlots, setTimeSlots] = useState([])

  useEffect(() => {
    loadData()

    async function loadData() {
      const responseClassrooms = await fetch('http://localhost:8000/api/v0/classrooms')
      setClassrooms((await responseClassrooms.json()).data)
      const responseTimeSlots = await fetch('http://localhost:8000/api/v0/time-slots')
      const rawTimeSlots = (await responseTimeSlots.json()).data
      setTimeSlots(
        rawTimeSlots.map((rawTimeSlot) => (
          {
            ...rawTimeSlot,
            end_datetime: dayjs(rawTimeSlot.end_datetime),
            start_datetime: dayjs(rawTimeSlot.start_datetime),
          }
        ))
      )
      const responseClassroomTimeSlots = await fetch('http://localhost:8000/api/v0/classroom-time-slots')
      setClassroomTimeSlots((await responseClassroomTimeSlots.json()).data)
    }
  }, [])

  const classroomTimeSlotLookupTable = classroomTimeSlots.reduce((acc, cts) => (
    {...acc, [cts.time_slot_id]: {...acc[cts.time_slot_id], [cts.classroom_id]: cts}}
  ), {})

  // const ctsByTimeSlot = classroomTimeSlots.reduce((acc, cts) => ({ ...acc, [cts.time_slot_id]: cts}))
  return (
    <div>
      <table className='table'>
        <thead>
          <tr>
            <th scope='col'></th>
            {classrooms.map((classroom) => (
              <th key={classroom.id} scope='col'>{classroom.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {timeSlots.map((timeSlot) => (
            <tr key={timeSlot.id}>
              <td
                dangerouslySetInnerHTML={{__html: timeSlotDisplayHtml(timeSlot)}}
                style={{whiteSpace: 'nowrap'}}
              />
              {classroomTimeSlots.length > 0
                ? classrooms.map((classroom) => <td>{getClassroomTimeSlot(timeSlot.id, classroom.id).id}</td>)
                : <td colSpan={classrooms.length} style={{textAlign: 'center'}}>
                  LOADING
                </td>
              }
            </tr>
          ))}
        </tbody>
      </table>
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

  function timeSlotDisplayHtml(timeSlot) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}<br>${startTimeDisplay} - ${endTimeDisplay}`
  }
}

export default App;
