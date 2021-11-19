/* Todo: implement me */

const DEFAULT_HEADERS = {
//   Cookie: ""
}

export function secureFetch(url, options) {
  options = {...options, headers: {...DEFAULT_HEADERS, ...options?.headers}}
  return fetch(url, options)
}
