import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import * as api from './api'

interface AuthState {
  user: api.User | null
  loading: boolean
  login: (email: string, password: string) => Promise<api.User>
  register: (input: api.RegisterInput) => Promise<api.User>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

// The session lives in an HttpOnly cookie set by the backend; the front end only keeps the
// public user info (never the password) in memory.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<api.User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .fetchMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const value: AuthState = {
    user,
    loading,
    login: async (email, password) => {
      const u = await api.login(email, password)
      setUser(u)
      return u
    },
    register: async (input) => {
      const u = await api.register(input)
      setUser(u)
      return u
    },
    logout: async () => {
      await api.logout()
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
