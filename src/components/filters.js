import {DAYS_OF_WEEK} from "../constants";
import {Form} from "react-bootstrap";

export function Filters(props) {
  const {filters, setFilters} = props

  return (
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
  )
}

function CheckboxFilter(props) {
  const {filters, filterKey, filterLabel, setFilters} = props

  return (
    <Form.Check
      checked={filters[filterKey]}
      id={`filter-${filterKey}`}
      label={filterLabel}
      onChange={() => setFilters({...filters, [filterKey]: !filters[filterKey]})}
      type='checkbox'
    />
  )
}

function TextFilter(props) {
  const {filters, filterKey, filterLabel, inputProps, setFilters} = props

  return (
    <Form.Group className='my-1' controlId={`filter-${filterKey}`}>
      <Form.Label className='mb-0'>{filterLabel}</Form.Label>
      <Form.Control
        {...inputProps}
        onChange={(event) => setFilters({...filters, [filterKey]: event.target.value})}
        value={filters[filterKey]}
      />
    </Form.Group>
  )
}
