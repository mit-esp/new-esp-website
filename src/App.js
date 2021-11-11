import {useEffect, useMemo, useState} from "react";
import dayjs from "dayjs";
import {useTable} from "react-table";

export default function App() {
  const [classrooms, setClassrooms] = useState([])
  const [classroomTimeSlots, setClassroomTimeSlots] = useState([])
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [timeSlots, setTimeSlots] = useState([])

  useEffect(() => {
    loadData()

    async function loadData() {
      const responseCourses = await fetch('http://localhost:8000/api/v0/courses')
      setCourses((await responseCourses.json()).data)
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
      setLoading(false)
    }
  }, [])

  const classroomTimeSlotLookupTable = classroomTimeSlots.reduce((acc, cts) => (
    {...acc, [cts.time_slot_id]: {...acc[cts.time_slot_id], [cts.classroom_id]: cts}}
  ), {})

  const data = timeSlots.map((timeSlot) => ({
    timeSlot: timeSlotDisplayHtml(timeSlot),
    ...classrooms.reduce((acc, classroom) => ({
      ...acc,
      [classroom.id]: getClassroomTimeSlot(timeSlot.id, classroom.id).id,
    }), {}),
  }))
  const columns = useMemo(() => {
    const classroomHeaders = classrooms.map((classroom) => ({
      Header: classroom.name,
      accessor: classroom.id,
      className: 'sticky',
    }))
    return [
      {
        Cell: ({row}) => <span dangerouslySetInnerHTML={{__html: row.original.timeSlot}} style={{whiteSpace: 'nowrap'}} />,
        Header: '',
        accessor: 'timeSlot',
      },
      ...classroomHeaders,
    ]
  }, [classrooms])


  return (
    <div className='scheduler'>
      <h1>Scheduler</h1>
      <div className='interface-wrapper'>
        <div className='calendar'>
          {loading
            ? <div>Loading...</div>
            : <Table columns={columns} data={data} style={{height: '100%', width: '100%'}} />
          }
        </div>
        <div className='courses'>
          <div className='card'>
            <div className='card-body'>
              <h5 className='card-title'>Courses</h5>
              <p className='card-subtitle mb-2 text-muted'>Please select a course</p>
              <div className='course-list'>
                {courses.length
                  ? courses.map((course) => (
                    <button className='btn btn-primary' key={course.id}>{course.name}</button>
                  ))
                  : <span>Loading...</span>
                }
              </div>
            </div>
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

  function timeSlotDisplayHtml(timeSlot) {
    const dateDisplay = timeSlot.start_datetime.format('ddd MMM D, YYYY')
    const startTimeDisplay = timeSlot.start_datetime.format('h:mma')
    const endTimeDisplay = timeSlot.end_datetime.format('h:mma')
    return `${dateDisplay}<br>${startTimeDisplay} - ${endTimeDisplay}`
  }
}

function Table({columns, data, style}) {
  const tableInstance = useTable({columns, data})
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = tableInstance

  return (
    <div className='table-responsive'>
      <table className='table' {...getTableProps()}>
        <thead>
        {headerGroups.map((headerGroup, index) => (
          <tr {...headerGroup.getHeaderGroupProps()} className={index === 0 ? 'sticky header' : ''}>
            {headerGroup.headers.map((column, index) => (
              <th {...column.getHeaderProps()} className={index === 0 ? 'sticky column header' : ''}>
                {column.render('Header')}
              </th>
            ))}
          </tr>
        ))}
        </thead>
        <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row)
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map((cell, index) => (
                <td {...cell.getCellProps()} className={index === 0 ? 'sticky column' : ''}>
                  {cell.render('Cell')}
                </td>
              ))}
            </tr>
          )
        })}
        </tbody>
      </table>
    </div>
  )
}
