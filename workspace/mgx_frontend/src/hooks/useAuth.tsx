import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { API_URL } from '../lib/api'

interface User {
  id: number
  username: string
  email: string
  avatar_url?: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateUser: (updates: { avatar_url?: string; email?: string }) => Promise<void>
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Load token and user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      setToken(storedToken)
      fetchUser(storedToken)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async (authToken: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token invalid, clear it
        localStorage.removeItem('auth_token')
        setToken(null)
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      localStorage.removeItem('auth_token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('auth_token', data.access_token)
  }

  const register = async (username: string, email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    const data = await response.json()
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('auth_token', data.access_token)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('auth_token')
  }

  const updateUser = async (updates: { avatar_url?: string; email?: string }) => {
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/auth/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updates)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Update failed')
    }

    const updatedUser = await response.json()
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        register,
        logout,
        updateUser,
        isAuthenticated: !!user && !!token,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

