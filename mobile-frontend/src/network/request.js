import axios from "axios"

const request = axios.create({
  baseURL: 'http://127.0.0.1',
  timeout: 5000
})

request.interceptors.request.use(config => {
  return config
}, err => {
  return err
})

request.interceptors.response.use(result => {
  return result.data
}, err => {
  return err
})

export default request;
