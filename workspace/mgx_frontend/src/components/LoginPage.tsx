import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Button } from './ui/button'
import { FileText, Mail, Lock, User, Sparkles } from 'lucide-react'

export function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(username, password)
      } else {
        if (!email) {
          setError('Email is required')
          setLoading(false)
          return
        }
        await register(username, email, password)
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-purple-50 to-pink-50 dark:from-purple-950 dark:via-pink-950 dark:to-purple-950 relative overflow-hidden">
      {/* Decorative background */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-64 h-64 bg-pink-300 dark:bg-pink-700 rounded-full blur-3xl animate-float" style={{ animationDelay: '0s' }}></div>
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-purple-300 dark:bg-purple-700 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-yellow-300 dark:bg-yellow-700 rounded-full blur-2xl animate-float" style={{ animationDelay: '0.5s' }}></div>
      </div>

      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="bg-white/90 dark:bg-purple-950/90 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-pink-200 dark:border-pink-800 p-8 pokemon-shadow">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full mb-4 pokemon-glow">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent mb-2">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h1>
            <p className="text-sm text-pink-600 dark:text-pink-400">
              {isLogin ? 'Sign in to continue' : 'Join us to get started'}
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-2">
                <User className="w-4 h-4 inline mr-1" />
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-2 focus:ring-pink-300 dark:focus:ring-pink-700 outline-none transition-all"
                placeholder="Enter your username"
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-2">
                  <Mail className="w-4 h-4 inline mr-1" />
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-2 focus:ring-pink-300 dark:focus:ring-pink-700 outline-none transition-all"
                  placeholder="Enter your email"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-2">
                <Lock className="w-4 h-4 inline mr-1" />
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-2 focus:ring-pink-300 dark:focus:ring-pink-700 outline-none transition-all"
                placeholder="Enter your password"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white pokemon-glow py-2"
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
            </Button>
          </form>

          {/* Toggle login/register */}
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
              }}
              className="text-sm text-pink-600 dark:text-pink-400 hover:text-pink-700 dark:hover:text-pink-300 transition-colors"
            >
              {isLogin ? (
                <>Don't have an account? <span className="font-semibold">Sign Up</span></>
              ) : (
                <>Already have an account? <span className="font-semibold">Sign In</span></>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

