import axios from 'axios'

const api = axios.create({
  baseURL: 'http://0.0.0.0/api/v1/',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api
