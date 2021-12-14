import {useEffect, useRef, useState} from "react";

const DEFAULT_HEADERS = {
//   Cookie: ""
}

export function getQueryParam(queryParam) {
  const urlSearchParams = new URLSearchParams(window.location.search)
  const params = Object.fromEntries(urlSearchParams.entries())
  return params[queryParam]
}

/**
 * Todo: implement me
 * */
export function secureFetch(url, options) {
  options = {...options, headers: {...DEFAULT_HEADERS, ...options?.headers}}
  return fetch(url, options)
}

export async function loadData(endpoint, setStateFunc, processFunc) {
  const response = await secureFetch(`${process.env.REACT_APP_API_BASE_URL}${endpoint}`)
  let data = (await response.json()).data
  if (processFunc !== undefined) {
    data = processFunc(data)
  }
  setStateFunc(data)
}

/**
 * Inspired by https://stackoverflow.com/a/66732282
 */
export function useStateWithCallback(initialState) {
  const callbackRef = useRef(null)
  const [state, setState] = useState(initialState);

  const setStateFunction = (state, callback) => {
    callbackRef.current = callback
    setState(state)
  }

  useEffect(() => {
    if (callbackRef.current) {
      callbackRef.current(state);
      callbackRef.current = null;
    }
  }, [state]);

  return [state, setStateFunction];
}
