import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { ScrollArea } from './ui/scroll-area'
import { Button } from './ui/button'
import { X, MessageSquare, Calendar, Trash2, Loader2 } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Conversation {
  id: number
  user_id: number
  project_id: number | null
  title: string
  messages: Array<{
    role: string
    roleName?: string
    content: string
    type?: string
    timestamp: string
  }>
  created_at: string
  updated_at: string
}

interface ConversationHistoryProps {
  onClose: () => void
}

export function ConversationHistory({ onClose }: ConversationHistoryProps) {
  const { user, token } = useAuth()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [deleting, setDeleting] = useState<number | null>(null)

  useEffect(() => {
    if (user && token) {
      console.log('📚 [History] User and token available, loading conversations...', {
        userId: user.id,
        username: user.username,
        hasToken: !!token
      })
      loadConversations()
    } else {
      console.log('📚 [History] Missing user or token', {
        hasUser: !!user,
        hasToken: !!token
      })
    }
  }, [user, token])

  const loadConversations = async () => {
    if (!token) {
      console.log('⏭️ [History] No token, skipping load')
      return
    }
    
    console.log('📚 [History] Loading conversations...', {
      tokenLength: token.length,
      tokenPreview: token.substring(0, 20) + '...',
      apiUrl: `${API_URL}/api/conversations`
    })
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/conversations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      console.log('📚 [History] Response status:', response.status, response.statusText)
      console.log('📚 [History] Response headers:', Object.fromEntries(response.headers.entries()))
      
      if (response.ok) {
        const data = await response.json()
        console.log('📚 [History] Loaded conversations:', data.length)
        setConversations(data)
      } else {
        const errorText = await response.text()
        console.error('📚 [History] Error response:', errorText)
        // Try to refresh token by fetching user info
        console.log('📚 [History] Attempting to refresh user info...')
        try {
          const userResponse = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          if (!userResponse.ok) {
            console.error('📚 [History] User info also failed, token may be invalid')
          } else {
            console.log('📚 [History] User info OK, but conversations failed - possible API issue')
          }
        } catch (e) {
          console.error('📚 [History] Failed to check user info:', e)
        }
      }
    } catch (error) {
      console.error('❌ [History] Failed to load conversations:', error)
      if (error instanceof Error) {
        console.error('Error details:', error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const deleteConversation = async (id: number) => {
    if (!token) return
    
    setDeleting(id)
    try {
      const response = await fetch(`${API_URL}/api/conversations/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setConversations(prev => prev.filter(c => c.id !== id))
        if (selectedConversation?.id === id) {
          setSelectedConversation(null)
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    } finally {
      setDeleting(null)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div 
        className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-4xl h-[80vh] pokemon-shadow border-2 border-pink-300 dark:border-pink-600 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-pink-200 dark:border-pink-800">
          <h2 className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
            对话历史记录
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Conversation List */}
          <div className="w-1/3 border-r border-pink-200 dark:border-pink-800 flex flex-col">
            <div className="p-3 border-b border-pink-200 dark:border-pink-800">
              <p className="text-sm text-pink-600 dark:text-pink-400">
                共 {conversations.length} 条记录
              </p>
            </div>
            <ScrollArea className="flex-1">
              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="w-6 h-6 animate-spin text-pink-600 dark:text-pink-400" />
                </div>
              ) : conversations.length === 0 ? (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>暂无历史记录</p>
                </div>
              ) : (
                <div className="p-2 space-y-2">
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => setSelectedConversation(conv)}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        selectedConversation?.id === conv.id
                          ? 'bg-pink-100 dark:bg-pink-900 border-2 border-pink-400 dark:border-pink-600'
                          : 'bg-pink-50 dark:bg-pink-950/30 border border-pink-200 dark:border-pink-800 hover:bg-pink-100 dark:hover:bg-pink-900'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-pink-900 dark:text-pink-100 truncate">
                            {conv.title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1 text-xs text-pink-600 dark:text-pink-400">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDate(conv.updated_at)}</span>
                          </div>
                          <p className="text-xs text-pink-500 dark:text-pink-500 mt-1">
                            {conv.messages.length} 条消息
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            if (confirm('确定要删除这条记录吗？')) {
                              deleteConversation(conv.id)
                            }
                          }}
                          disabled={deleting === conv.id}
                          className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1"
                        >
                          {deleting === conv.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          {/* Conversation Detail */}
          <div className="flex-1 flex flex-col">
            {selectedConversation ? (
              <>
                <div className="p-4 border-b border-pink-200 dark:border-pink-800">
                  <h3 className="font-semibold text-pink-900 dark:text-pink-100">
                    {selectedConversation.title}
                  </h3>
                  <p className="text-sm text-pink-600 dark:text-pink-400 mt-1">
                    {formatDate(selectedConversation.updated_at)}
                  </p>
                </div>
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {selectedConversation.messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-pink-100 dark:bg-pink-900 ml-auto max-w-[80%]'
                            : 'bg-purple-100 dark:bg-purple-900 mr-auto max-w-[80%]'
                        }`}
                      >
                        <div className="text-xs font-medium text-pink-700 dark:text-pink-300 mb-1">
                          {msg.role === 'user' ? '你' : (msg.roleName || '助手')}
                        </div>
                        <div className="text-sm text-pink-900 dark:text-pink-100 whitespace-pre-wrap">
                          {msg.content}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="p-4 border-t border-pink-200 dark:border-pink-800">
                  <Button
                    onClick={() => {
                      // Load conversation to chat panel
                      const loadFn = (window as any).loadConversationToChat
                      if (loadFn) {
                        loadFn(
                          selectedConversation.messages,
                          selectedConversation.id,
                          selectedConversation.title,
                          selectedConversation.project_id,
                          (selectedConversation as any).extra_data
                        )
                      }
                      onClose()
                    }}
                    className="w-full pokemon-gradient hover:pokemon-glow text-white"
                  >
                    加载到聊天面板 {selectedConversation.project_id && '（含代码）'}
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>选择一条记录查看详情</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

