import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = 'rag_access_token'
const USER_KEY = 'rag_user'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null }
  })
  const [credStatus, setCredStatus] = useState(null) // {configured, has_qdrant, has_openrouter, is_admin}
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState(null)

  const apiFetch = useCallback(async (path, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    }
    const t = localStorage.getItem(TOKEN_KEY)
    if (t) headers['Authorization'] = `Bearer ${t}`
    const res = await fetch(path, { ...options, headers })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Request failed')
    }
    return res.json()
  }, [])

  const fetchCredStatus = useCallback(async () => {
    try {
      const data = await apiFetch('/api/auth/credentials/status')
      setCredStatus(data)
      return data
    } catch {
      setCredStatus(null)
      return null
    }
  }, [apiFetch])

  // Handle OAuth redirect token in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const oauthToken = params.get('token')
    const type = params.get('type')
    if (oauthToken && type === 'oauth') {
      // Fetch user profile with this token
      window.history.replaceState({}, '', '/')
      fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${oauthToken}`, 'Content-Type': 'application/json' },
      })
        .then(r => r.json())
        .then(u => {
          localStorage.setItem(TOKEN_KEY, oauthToken)
          localStorage.setItem(USER_KEY, JSON.stringify(u))
          setToken(oauthToken)
          setUser(u)
        })
        .catch(console.error)
    }
  }, [])

  // Fetch cred status whenever user logs in
  useEffect(() => {
    if (token && user) {
      fetchCredStatus()
    } else {
      setCredStatus(null)
    }
  }, [token, user, fetchCredStatus])

  const login = async (email, password) => {
    setAuthLoading(true)
    setAuthError(null)
    try {
      const data = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem(TOKEN_KEY, data.access_token)
      const userObj = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        is_admin: data.is_admin,
      }
      localStorage.setItem(USER_KEY, JSON.stringify(userObj))
      setToken(data.access_token)
      setUser(userObj)
      return data
    } catch (e) {
      setAuthError(e.message)
      throw e
    } finally {
      setAuthLoading(false)
    }
  }

  const signup = async (email, password, fullName) => {
    setAuthLoading(true)
    setAuthError(null)
    try {
      const data = await apiFetch('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name: fullName }),
      })
      localStorage.setItem(TOKEN_KEY, data.access_token)
      const userObj = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        is_admin: data.is_admin,
      }
      localStorage.setItem(USER_KEY, JSON.stringify(userObj))
      setToken(data.access_token)
      setUser(userObj)
      return data
    } catch (e) {
      setAuthError(e.message)
      throw e
    } finally {
      setAuthLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
    setCredStatus(null)
  }

  const saveCredentials = async (qdrantUrl, qdrantApiKey, openrouterApiKey) => {
    const data = await apiFetch('/api/auth/credentials', {
      method: 'POST',
      body: JSON.stringify({
        qdrant_url: qdrantUrl,
        qdrant_api_key: qdrantApiKey,
        openrouter_api_key: openrouterApiKey,
      }),
    })
    await fetchCredStatus()
    return data
  }

  const getAuthHeader = useCallback(() => {
    const t = localStorage.getItem(TOKEN_KEY)
    return t ? { Authorization: `Bearer ${t}` } : {}
  }, [])

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        credStatus,
        authLoading,
        authError,
        login,
        signup,
        logout,
        saveCredentials,
        fetchCredStatus,
        getAuthHeader,
        clearAuthError: () => setAuthError(null),
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
