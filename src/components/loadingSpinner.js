import {Spinner} from "react-bootstrap";

export function LoadingSpinner(props) {
  const {centered} = props
  return (
    <div className={`loading-spinner ${centered ? 'centered' : ''}`}>
      <Spinner animation="border" variant="primary" />
      <span className='text'>Loading...</span>
    </div>
  )
}
