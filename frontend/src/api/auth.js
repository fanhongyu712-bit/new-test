import request from './request'

export const authApi = {
  login(username, password) {
    return request.post('/auth/login', null, {
      params: { username, password }
    })
  },

  register(data) {
    return request.post('/auth/register', data)
  },

  logout() {
    return request.post('/auth/logout')
  },

  getCurrentUser() {
    return request.get('/users/me')
  }
}

export const login = authApi.login
export const register = authApi.register
export const logout = authApi.logout
export const getCurrentUser = authApi.getCurrentUser
export const getUserList = (params) => request.get('/users', { params })
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
