import axios from 'axios'
// 以后前端所有请求都通过 apiClient 发给你的 FastAPI 后端。
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
// 登录成功后，我们会把 Token 保存到浏览器的 localStorage。
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default apiClient