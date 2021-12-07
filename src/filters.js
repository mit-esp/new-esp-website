import {Form} from "react-bootstrap";


export function CheckboxFilter(props) {
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

export function TextFilter(props) {
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
