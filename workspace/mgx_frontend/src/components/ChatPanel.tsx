import { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Loader2, Brain, ChevronDown, MessageSquarePlus } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { useAuth } from '../hooks/useAuth'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { ScrollArea } from './ui/scroll-area'
import { API_URL } from '../lib/api'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  roleName?: string
  content: string
  type?: 'thinking' | 'working' | 'message' | 'complete'
  timestamp: Date
}

export function ChatPanel() {
  const [idea, setIdea] = useState('')
  const [investment, setInvestment] = useState(5.0)
  const { currentTask, isGenerating, startGeneration, chatMessages, loadProjectFiles, clearFiles } = useTask()
  const { user, token } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const [showScrollToBottom, setShowScrollToBottom] = useState(false)
  const [userScrolled, setUserScrolled] = useState(false)
  const lastMessageCountRef = useRef(0)
  const [savingHistory, setSavingHistory] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    setShowScrollToBottom(false)
    setUserScrolled(false)
  }
  
  // Check if user is near bottom of scroll area
  const checkScrollPosition = () => {
    if (!scrollAreaRef.current) return
    
    const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
    if (!scrollElement) return
    
    const { scrollTop, scrollHeight, clientHeight } = scrollElement as HTMLElement
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100 // 100px threshold
    
    if (isNearBottom) {
      setShowScrollToBottom(false)
      setUserScrolled(false)
    } else {
      // Only show scroll button if there are new messages
      if (messages.length > lastMessageCountRef.current) {
        setShowScrollToBottom(true)
      }
    }
  }
  
  // Only auto-scroll when user sends a message (not when receiving messages)
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.role === 'user') {
      // User sent a message, auto-scroll to see the response
      setTimeout(() => scrollToBottom(), 100)
    }
  }, [messages.filter(m => m.role === 'user').length])
  
  // Track message count changes
  useEffect(() => {
    if (messages.length > lastMessageCountRef.current && !userScrolled) {
      // New messages arrived, check if we should auto-scroll
      setTimeout(() => {
        checkScrollPosition()
      }, 100)
    }
    lastMessageCountRef.current = messages.length
  }, [messages.length, userScrolled])
  
  // Set up scroll listener to detect user scrolling
  useEffect(() => {
    if (!scrollAreaRef.current) return
    
    const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
    if (!scrollElement) return
    
    const handleScroll = () => {
      setUserScrolled(true)
      checkScrollPosition()
    }
    
    scrollElement.addEventListener('scroll', handleScroll, { passive: true })
    return () => {
      scrollElement.removeEventListener('scroll', handleScroll)
    }
  }, [])
  
  // IMPORTANT: Process chatMessages immediately (from direct queue, not from currentTask)
  useEffect(() => {
    console.log('💬 [ChatPanel] chatMessages changed, length:', chatMessages.length, chatMessages)
    
    // If chatMessages queue is cleared (new task started), clear local messages too
    // But only if we have a current task that just started
    if (chatMessages.length === 0 && messages.length > 0 && currentTask) {
      const taskJustStarted = currentTask.current_stage === 'Initializing' && 
                              currentTask.progress === 0
      if (taskJustStarted) {
        console.log('💬 [ChatPanel] New task started (chatMessages cleared), clearing local messages')
        setMessages([])
        return
      }
    }
    
    if (chatMessages.length > 0) {
      setMessages(prev => {
        console.log('💬 [ChatPanel] Processing chatMessages, current messages count:', prev.length)
        const newMessages: ChatMessage[] = []
        // Process chatMessages in order, but only add new ones
        chatMessages.forEach(chatMsg => {
          // Check if this chat message already exists (by content, not just role)
          const exists = prev.some(msg => 
            msg.role === 'assistant' && 
            msg.content === chatMsg.content
          )
          if (!exists) {
            console.log('💬 [ChatPanel] Adding chat message from queue:', {
              role: chatMsg.role,
              content: chatMsg.content.substring(0, 50),
              id: chatMsg.id
            })
            newMessages.push({
              id: chatMsg.id,
              role: 'assistant',
              roleName: chatMsg.role,
              content: chatMsg.content,
              type: 'message',
              timestamp: chatMsg.timestamp
            })
          } else {
            console.log('💬 [ChatPanel] Chat message already exists, skipping:', chatMsg.role, chatMsg.content.substring(0, 50))
          }
        })
        if (newMessages.length > 0) {
          console.log('💬 [ChatPanel] Adding', newMessages.length, 'new messages. Total will be:', prev.length + newMessages.length)
          // IMPORTANT: Preserve order - add new messages at the end, but maintain chronological order
          // Sort all messages by timestamp to ensure correct order
          const allMessages = [...prev, ...newMessages]
          allMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
          return allMessages
        }
        return prev
      })
    }
  }, [chatMessages])
  
  // Update messages based on task updates
  useEffect(() => {
    if (!currentTask) {
      // Only clear messages if task is completely gone (not just updating)
      // Don't clear on every update to prevent flickering
      return
    }
    
    // Add user message (but don't clear existing messages, especially chat messages)
    if (currentTask.idea) {
      setMessages(prev => {
        const hasUserMsg = prev.some(msg => msg.role === 'user' && msg.content === currentTask.idea)
        if (!hasUserMsg) {
          // Add user message at the beginning, but keep all existing messages
          return [{
            id: 'user-0',
            role: 'user' as const,
            content: currentTask.idea,
            timestamp: new Date(currentTask.created_at)
          }, ...prev]
        }
        return prev
      })
    }
    
    // Add assistant messages based on task updates
    // IMPORTANT: Process messages even if only message field is set (for chat messages)
    if (currentTask.message || currentTask.current_stage) {
        // Check if this is a chat_message type (human-like communication)
        // Check for chat message indicators - be more lenient
        const isChatMessage = currentTask.message && (
          currentTask.message.includes('👋') || 
          currentTask.message.includes('你好') ||
          currentTask.message.includes('我是') ||
          currentTask.message.includes('接下来') ||
          currentTask.message.includes('交给') ||
          currentTask.message.includes('✅') ||
          currentTask.message.includes('🎉') ||
          currentTask.message.includes('产品经理') ||
          currentTask.message.includes('系统架构师') ||
          currentTask.message.includes('软件工程师') ||
          currentTask.message.includes('完成了')
        )
        
        // Debug: Log message processing
        if (currentTask.message && isChatMessage) {
          console.log('💬 [ChatPanel] Processing chat message:', {
            role: currentTask.role,
            message: currentTask.message.substring(0, 100),
            isChatMessage
          })
        }
        
        // For chat messages, prioritize message over current_stage
        // For other messages, prefer current_stage for status messages
        let newContent = ''
        if (isChatMessage && currentTask.message) {
          // Chat messages should use the message content directly
          newContent = currentTask.message
        } else {
          // Regular status messages use current_stage or message
          newContent = currentTask.current_stage || currentTask.message || ''
          
          // Filter out file content - only show status messages
          if (currentTask.message && (
            currentTask.message.includes('FILE:') || 
            currentTask.message.includes('```') ||
            currentTask.message.length > 200 // Long messages are likely file content
          )) {
            newContent = currentTask.current_stage || `${currentTask.role} is working...`
          }
        }
        
        // Determine message type
        let type: 'thinking' | 'working' | 'message' | 'complete' = 'message'
        if (isChatMessage) {
          type = 'message' // Chat messages are regular messages
        } else if (currentTask.current_stage?.toLowerCase().includes('thinking')) {
          type = 'thinking'
        } else if (currentTask.current_stage?.toLowerCase().includes('executing') || 
                   currentTask.current_stage?.toLowerCase().includes('working') ||
                   currentTask.current_stage?.toLowerCase().includes('starting')) {
          type = 'working'
        } else if (currentTask.status === 'completed') {
          type = 'complete'
        }
        
        // For chat messages, always add as new message (don't update existing)
        // BUT: Skip if this message is already in chatMessages queue (to avoid duplicate processing)
        if (isChatMessage && newContent) {
          // Check if this message is already in chatMessages queue (processed by queue handler)
          const alreadyInQueue = chatMessages.some(cm => 
            cm.role === currentTask.role && 
            cm.content === newContent
          )
          
          // Also check if it's already in messages state
          const alreadyInMessages = messages.some(msg => 
            msg.role === 'assistant' && 
            msg.content === newContent
          )
          
          // If it's in the queue or already in messages, skip (to avoid duplicate/flickering)
          if (alreadyInQueue || alreadyInMessages) {
            console.log('💬 [ChatPanel] Chat message already processed, skipping task update handler:', newContent.substring(0, 50))
            return
          }
          
          console.log('💬 [ChatPanel] Adding chat message to UI:', {
            role: currentTask.role,
            content: newContent.substring(0, 50) + '...',
            fullContent: newContent,
            currentMessagesCount: messages.length
          })
          setMessages(prev => {
            // Double-check it doesn't exist (race condition protection)
            const exists = prev.some(msg => 
              msg.role === 'assistant' && 
              msg.content === newContent
            )
            if (!exists) {
              console.log('💬 [ChatPanel] Message is new, adding to messages array. New count:', prev.length + 1)
              const newMessage = {
                id: `assistant-${Date.now()}-${Math.random()}`,
                role: 'assistant' as const,
                roleName: currentTask.role || 'Assistant',
                content: newContent,
                type: 'message' as const,
                timestamp: new Date()
              }
              console.log('💬 [ChatPanel] New message object:', newMessage)
              // Sort by timestamp to maintain order
              const allMessages = [...prev, newMessage]
              allMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
              return allMessages
            } else {
              console.log('💬 [ChatPanel] Message already exists, skipping. Existing messages:', prev.length)
            }
            return prev
          })
        } else {
          // For working/thinking status messages, find and update existing message for this role
          // This prevents duplicate status messages
          setMessages(prev => {
            // Find existing message for this role with same type (working/thinking)
            const existingMsgIndex = prev.findIndex(msg => 
              msg.role === 'assistant' && 
              msg.roleName === currentTask.role &&
              (type === 'working' || type === 'thinking') &&
              (msg.type === type || msg.type === 'working' || msg.type === 'thinking')
            )
            
            if (existingMsgIndex >= 0) {
              // Update existing message with new content
              console.log('💬 [ChatPanel] Updating existing', type, 'message for', currentTask.role)
              return prev.map((msg, idx) => {
                if (idx === existingMsgIndex) {
                  return { ...msg, content: newContent, type }
                }
                return msg
              })
            } else {
              // Check if similar content already exists (to avoid duplicates)
              const similarExists = prev.some(msg => 
                msg.role === 'assistant' && 
                msg.roleName === currentTask.role &&
                msg.content === newContent
              )
              
              if (!similarExists) {
                // Add new message
                console.log('💬 [ChatPanel] Adding new', type, 'message for', currentTask.role)
                return [...prev, {
                  id: `assistant-${Date.now()}-${Math.random()}`,
                  role: 'assistant',
                  roleName: currentTask.role,
                  content: newContent,
                  type,
                  timestamp: new Date()
                }]
              } else {
                console.log('💬 [ChatPanel] Similar message already exists, skipping:', newContent.substring(0, 50))
                return prev
              }
            }
          })
        }
      }
  }, [currentTask])

  // Auto-save conversation history (debounced)
  const saveConversationHistory = async (isUpdate = false) => {
    if (!user || !token || messages.length === 0) {
      console.log('⏭️ [Save] Skipping save: user=', !!user, 'token=', !!token, 'messages.length=', messages.length)
      return
    }
    
    console.log('💾 [Save] Starting save...', {
      userId: user.id,
      messagesCount: messages.length,
      isUpdate,
      conversationId: currentConversationId
    })
    
    setSavingHistory(true)
    try {
      const conversationData = {
        user_id: user.id,
        project_id: null, // We'll use task_id from extra_data instead
        title: idea || `Conversation ${new Date().toLocaleDateString()}`,
        messages: messages.map(msg => ({
          role: msg.role,
          roleName: msg.roleName,
          content: msg.content,
          type: msg.type,
          timestamp: msg.timestamp.toISOString()
        })),
        extra_data: currentTask?.task_id ? { task_id: currentTask.task_id } : null
      }
      
      console.log('💾 [Save] Sending request...', {
        url: isUpdate && currentConversationId 
          ? `${API_URL}/api/conversations/${currentConversationId}`
          : `${API_URL}/api/conversations`,
        method: isUpdate ? 'PUT' : 'POST',
        messagesCount: conversationData.messages.length
      })
      
      let response
      if (isUpdate && currentConversationId) {
        // Update existing conversation
        response = await fetch(`${API_URL}/api/conversations/${currentConversationId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: conversationData.title,
            messages: conversationData.messages
          })
        })
      } else {
        // Create new conversation
        response = await fetch(`${API_URL}/api/conversations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(conversationData)
        })
      }
      
      console.log('💾 [Save] Response status:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('💾 [Save] Error response:', errorText)
        throw new Error(`Failed to save conversation: ${response.status} ${errorText}`)
      }
      
      const data = await response.json()
      console.log('💾 [Save] Success!', {
        conversationId: data.id,
        title: data.title,
        messagesCount: data.messages?.length || 0
      })
      
      if (!currentConversationId && data.id) {
        setCurrentConversationId(data.id)
        console.log('💾 [Save] Set conversation ID:', data.id)
      }
      
      console.log('✅ Conversation history saved', isUpdate ? '(updated)' : '(created)')
    } catch (error) {
      console.error('❌ Failed to save conversation history:', error)
      if (error instanceof Error) {
        console.error('Error details:', error.message)
      }
    } finally {
      setSavingHistory(false)
    }
  }
  
  // Auto-save when messages change (debounced)
  useEffect(() => {
    if (!user || !token || messages.length === 0) {
      console.log('⏭️ [Auto-save] Skipping: user=', !!user, 'token=', !!token, 'messages.length=', messages.length)
      return
    }
    
    console.log('💾 [Auto-save] Scheduling save in 2 seconds...', {
      messagesCount: messages.length,
      conversationId: currentConversationId,
      isUpdate: !!currentConversationId
    })
    
    // Debounce: save 2 seconds after last message change
    const timer = setTimeout(() => {
      console.log('💾 [Auto-save] Executing save now...')
      saveConversationHistory(!!currentConversationId)
    }, 2000)
    
    return () => {
      console.log('💾 [Auto-save] Timer cleared')
      clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages.length, user, token, currentConversationId])
  
  // Reset conversation ID when starting new task
  useEffect(() => {
    if (currentTask?.status === 'pending' && currentTask?.current_stage === 'Initializing') {
      setCurrentConversationId(null)
    }
  }, [currentTask?.status, currentTask?.current_stage])
  
  // Load conversation from history - use useCallback to maintain stable reference
  const loadConversation = useCallback((historyMessages: Array<{
    role: string
    roleName?: string
    content: string
    type?: string
    timestamp: string
  }>, conversationId: number, conversationTitle: string, projectId?: number | null, extraData?: any) => {
    // Convert history messages to ChatMessage format
    const loadedMessages: ChatMessage[] = historyMessages.map((msg, idx) => ({
      id: `loaded-${conversationId}-${idx}`,
      role: msg.role as 'user' | 'assistant',
      roleName: msg.roleName,
      content: msg.content,
      type: msg.type as 'thinking' | 'working' | 'message' | 'complete' | undefined,
      timestamp: new Date(msg.timestamp)
    }))
    
    setMessages(loadedMessages)
    setCurrentConversationId(conversationId)
    setIdea(conversationTitle)
    
    // Load project files - try task_id from extra_data first, then project_id
    const taskId = extraData?.task_id || (projectId ? String(projectId) : null)
    if (taskId) {
      console.log('📁 [Chat] Loading project files for task_id:', taskId)
      loadProjectFiles(taskId)
    } else {
      console.log('⏭️ [Chat] No task_id or project_id found, skipping file load')
    }
    
    // Scroll to bottom
    setTimeout(() => scrollToBottom(), 100)
  }, [loadProjectFiles])
  
  // Expose loadConversation function via window for ConversationHistory component
  useEffect(() => {
    (window as any).loadConversationToChat = loadConversation
    return () => {
      delete (window as any).loadConversationToChat
    }
  }, [loadConversation])

  const handleNewChat = () => {
    // Clear all chat state
    setMessages([])
    setCurrentConversationId(null)
    setIdea('')
    setUserScrolled(false)
    setShowScrollToBottom(false)
    lastMessageCountRef.current = 0
    
    // Clear all files and task state
    clearFiles()
    
    console.log('💬 [Chat] New chat started - cleared all messages, state, and files')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!idea.trim() || isGenerating) return
    
    // Clear messages and conversation ID when starting a new generation
    setMessages([])
    setCurrentConversationId(null)
    await startGeneration(idea, investment)
  }

  // Get Pokemon avatar image path for each role (using Eevee evolutions theme)
  const getPokemonAvatar = (roleName?: string) => {
    if (roleName === 'Alice' || roleName === 'ProductManager') {
      return '/pokemon/sylveon.png' // Sylveon - cute and friendly Product Manager
    }
    if (roleName === 'Bob' || roleName === 'Architect') {
      return '/pokemon/espeon.png' // Espeon - wise and intelligent Architect  
    }
    if (roleName === 'Charlie' || roleName === 'Engineer') {
      return '/pokemon/umbreon.png' // Umbreon - creative and technical Engineer
    }
    // Default avatar for assistant messages without specific role - Kirby (星之卡比)
    // Try local file first, fallback to online image
    // You can add your own kirby.png to public/pokemon/ directory
    return '/pokemon/kirby.png' // Kirby avatar - add your own image or it will show emoji fallback
  }
  
  // Get Pokemon avatar background color (matching Eevee evolution themes)
  const getPokemonAvatarBg = (roleName?: string) => {
    if (roleName === 'Alice' || roleName === 'ProductManager') {
      return 'bg-pink-100 dark:bg-pink-900 border-pink-300 dark:border-pink-700' // Sylveon - pink/white theme
    }
    if (roleName === 'Bob' || roleName === 'Architect') {
      return 'bg-purple-100 dark:bg-purple-900 border-purple-300 dark:border-purple-700' // Espeon - purple theme
    }
    if (roleName === 'Charlie' || roleName === 'Engineer') {
      return 'bg-slate-100 dark:bg-slate-800 border-yellow-400 dark:border-yellow-600' // Umbreon - black/yellow theme
    }
    return 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700'
  }
  
  // Get message type style
  const getMessageTypeStyle = (msg: ChatMessage) => {
    const isIntro = msg.content.includes('👋') || msg.content.includes('你好') || msg.content.includes('我是')
    const isComplete = msg.content.includes('✅') || msg.content.includes('完成了') || msg.content.includes('🎉')
    const isHandoff = msg.content.includes('接下来') || msg.content.includes('交给')
    
    if (isIntro) {
      // Introduction messages - pink-purple gradient with sparkle effect
      return 'border-2 border-pink-300 dark:border-pink-600 bg-gradient-to-br from-pink-100 via-purple-100 to-pink-100 dark:from-pink-900 dark:via-purple-900 dark:to-pink-900 pokemon-shadow animate-sparkle'
    }
    if (isComplete || isHandoff) {
      // Completion/handoff messages - pink-purple gradient
      return 'border-2 border-purple-300 dark:border-purple-600 bg-gradient-to-br from-purple-100 via-pink-100 to-purple-100 dark:from-purple-900 dark:via-pink-900 dark:to-purple-900 pokemon-shadow'
    }
    if (msg.type === 'thinking') {
      // Thinking messages - purple gradient
      return 'border-2 border-purple-300 dark:border-purple-600 bg-gradient-to-br from-purple-50 via-purple-100 to-pink-50 dark:from-purple-900 dark:via-purple-800 dark:to-pink-900 pokemon-shadow'
    }
    if (msg.type === 'working') {
      // Working messages - pink gradient
      return 'border-2 border-pink-300 dark:border-pink-600 bg-gradient-to-br from-pink-50 via-pink-100 to-purple-50 dark:from-pink-900 dark:via-pink-800 dark:to-purple-900 pokemon-shadow'
    }
    // Regular chat messages - soft pink-purple gradient
    return 'pokemon-shadow'
  }

  return (
    <div className="w-full h-full border-r border-pink-200 dark:border-pink-800 flex flex-col bg-gradient-to-b from-white/80 via-pink-50/80 to-purple-50/80 dark:from-purple-950/80 dark:via-pink-950/80 dark:to-purple-950/80 backdrop-blur-sm min-h-0">
      <div className="flex-shrink-0 p-4 border-b border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-900 dark:to-purple-900 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold text-lg bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">💬 Chat</h2>
          {savingHistory && (
            <div className="flex items-center gap-1 text-xs text-pink-600 dark:text-pink-400">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>保存中...</span>
            </div>
          )}
        </div>
        <Button
          onClick={handleNewChat}
          size="sm"
          variant="ghost"
          className="gap-2 text-pink-700 dark:text-pink-300 hover:bg-pink-200 dark:hover:bg-pink-800 rounded-xl transition-all transform hover:scale-105"
          disabled={isGenerating}
          title="开始新对话"
        >
          <MessageSquarePlus className="w-4 h-4" />
          <span className="hidden sm:inline">New Chat</span>
        </Button>
      </div>
      
      <div className="flex-1 min-h-0 overflow-hidden relative">
        <ScrollArea 
          ref={scrollAreaRef}
          className="h-full p-4"
        >
        <div className="space-y-4">
          {/* Initial welcome screen with agent avatars */}
          {messages.length === 0 && !currentTask && (
            <div className="flex flex-col items-center justify-center py-12 px-4 space-y-6 animate-fade-in">
              {/* Pokemon-style decorative elements */}
              <div className="relative w-full max-w-xs">
                <div className="absolute -top-4 -left-4 w-16 h-16 bg-pink-200 dark:bg-pink-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '0s' }}></div>
                <div className="absolute -top-2 -right-6 w-12 h-12 bg-purple-200 dark:bg-purple-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '0.5s' }}></div>
                <div className="absolute -bottom-4 left-8 w-10 h-10 bg-yellow-200 dark:bg-yellow-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '1s' }}></div>
                
                {/* Main welcome card */}
                <div className="relative bg-gradient-to-br from-pink-100 via-purple-100 to-pink-100 dark:from-pink-900 dark:via-purple-900 dark:to-pink-900 rounded-2xl p-6 border-2 border-pink-300 dark:border-pink-600 pokemon-shadow">
                  <div className="text-center mb-6">
                    <div className="text-5xl mb-2 animate-bounce">⚡</div>
                    <h3 className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
                      Welcome to MGX!
                    </h3>
                    <p className="text-sm text-pink-700 dark:text-pink-300 mt-2">
                      Your AI development team is ready
                    </p>
                  </div>
                  
                  {/* Three agents display */}
          <div className="space-y-4">
                    <div className="text-xs font-semibold text-pink-600 dark:text-pink-400 text-center mb-3">
                      Meet Your Team
                    </div>
                    
                    {/* Alice - Product Manager (Sylveon) */}
                    <div className="flex items-center gap-3 bg-white/60 dark:bg-purple-950/60 rounded-xl p-3 border border-pink-200 dark:border-pink-700 hover:scale-105 transition-transform pokemon-shadow">
                      <div className="flex-shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-pink-200 to-pink-300 dark:from-pink-700 dark:to-pink-800 border-2 border-pink-400 dark:border-pink-500 flex items-center justify-center shadow-md overflow-hidden">
                        <img 
                          src="/pokemon/sylveon.png" 
                          alt="Sylveon (Alice)"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement
                            target.style.display = 'none'
                            const parent = target.parentElement
                            if (parent) {
                              parent.innerHTML = '🌸'
                              parent.className += ' text-3xl'
                            }
                          }}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm text-pink-900 dark:text-pink-100">Alice</div>
                        <div className="text-xs text-pink-600 dark:text-pink-400">Product Manager</div>
                        <div className="text-xs text-pink-500 dark:text-pink-500 mt-1">Planning & Requirements</div>
                      </div>
                    </div>
                    
                    {/* Bob - Architect (Espeon) */}
                    <div className="flex items-center gap-3 bg-white/60 dark:bg-purple-950/60 rounded-xl p-3 border border-purple-200 dark:border-purple-700 hover:scale-105 transition-transform pokemon-shadow">
                      <div className="flex-shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-purple-200 to-purple-300 dark:from-purple-700 dark:to-purple-800 border-2 border-purple-400 dark:border-purple-500 flex items-center justify-center shadow-md overflow-hidden">
                        <img 
                          src="/pokemon/espeon.png" 
                          alt="Espeon (Bob)"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement
                            target.style.display = 'none'
                            const parent = target.parentElement
                            if (parent) {
                              parent.innerHTML = '🧠'
                              parent.className += ' text-3xl'
                            }
                          }}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm text-purple-900 dark:text-purple-100">Bob</div>
                        <div className="text-xs text-purple-600 dark:text-purple-400">System Architect</div>
                        <div className="text-xs text-purple-500 dark:text-purple-500 mt-1">Design & Architecture</div>
                      </div>
                    </div>
                    
                    {/* Charlie - Engineer (Umbreon) */}
                    <div className="flex items-center gap-3 bg-white/60 dark:bg-purple-950/60 rounded-xl p-3 border border-yellow-200 dark:border-yellow-700 hover:scale-105 transition-transform pokemon-shadow">
                      <div className="flex-shrink-0 w-14 h-14 rounded-full bg-gradient-to-br from-slate-200 to-yellow-200 dark:from-slate-700 dark:to-yellow-800 border-2 border-yellow-400 dark:border-yellow-500 flex items-center justify-center shadow-md overflow-hidden">
                        <img 
                          src="/pokemon/umbreon.png" 
                          alt="Umbreon (Charlie)"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement
                            target.style.display = 'none'
                            const parent = target.parentElement
                            if (parent) {
                              parent.innerHTML = '⚡'
                              parent.className += ' text-3xl'
                            }
                          }}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm text-slate-900 dark:text-slate-100">Charlie</div>
                        <div className="text-xs text-yellow-600 dark:text-yellow-400">Software Engineer</div>
                        <div className="text-xs text-yellow-500 dark:text-yellow-500 mt-1">Code Implementation</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Decorative sparkles */}
                  <div className="absolute top-2 right-2 text-2xl opacity-20 animate-pulse">✨</div>
                  <div className="absolute bottom-2 left-2 text-xl opacity-20 animate-pulse" style={{ animationDelay: '0.5s' }}>⭐</div>
                </div>
              </div>
              
              {/* Instructions */}
              <div className="text-center space-y-2 max-w-xs">
                <p className="text-sm text-pink-600 dark:text-pink-400 font-medium">
                  💡 Enter your project idea below to get started!
                </p>
                <p className="text-xs text-pink-500 dark:text-pink-500">
                  Your team will work together to bring it to life
                </p>
              </div>
            </div>
          )}
          
          {messages.map((msg) => {
            const getRoleColor = () => {
              if (msg.roleName === 'ProductManager') return 'bg-gradient-to-br from-pink-50 via-pink-100 to-purple-50 dark:from-pink-900 dark:via-pink-800 dark:to-purple-900 border-pink-300 dark:border-pink-600'
              if (msg.roleName === 'Architect') return 'bg-gradient-to-br from-purple-50 via-purple-100 to-pink-50 dark:from-purple-900 dark:via-purple-800 dark:to-pink-900 border-purple-300 dark:border-purple-600'
              if (msg.roleName === 'Engineer') return 'bg-gradient-to-br from-slate-50 via-purple-50 to-slate-50 dark:from-slate-800 dark:via-purple-900 dark:to-slate-800 border-yellow-300 dark:border-yellow-600'
              return 'bg-gradient-to-br from-pink-50 to-purple-50 dark:from-pink-900 dark:to-purple-900'
            }
            
            if (msg.role === 'user') {
              return (
                <div key={msg.id} className="bg-gradient-to-br from-pink-200 via-purple-200 to-pink-200 dark:from-pink-800 dark:via-purple-800 dark:to-pink-800 rounded-2xl p-4 border-2 border-pink-300 dark:border-pink-600 pokemon-shadow">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl animate-float">👤</span>
                    <p className="text-sm font-semibold text-pink-900 dark:text-pink-100">You</p>
                  </div>
                  <p className="text-sm leading-relaxed text-pink-900 dark:text-pink-100">{msg.content}</p>
                </div>
              )
            }
            
            const pokemonAvatarPath = getPokemonAvatar(msg.roleName)
            const pokemonAvatarBg = getPokemonAvatarBg(msg.roleName)
            const messageTypeStyle = getMessageTypeStyle(msg)
            const roleDisplayName = msg.roleName === 'Alice' ? 'Alice (Product Manager)' 
              : msg.roleName === 'Bob' ? 'Bob (Architect)'
              : msg.roleName === 'Charlie' ? 'Charlie (Engineer)'
              : msg.roleName || 'Assistant'
            
            return (
              <div key={msg.id} className={`rounded-xl p-4 border ${getRoleColor()} ${messageTypeStyle} transition-all hover:shadow-lg`}>
                <div className="flex items-start gap-3 mb-2">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full ${pokemonAvatarBg} flex items-center justify-center border-2 shadow-md hover:scale-110 transition-transform overflow-hidden`}>
                    {/* pokemonAvatarPath is always set now (returns Kirby URL for default assistant) */}
                    <img 
                      src={pokemonAvatarPath} 
                      alt={roleDisplayName}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to emoji if image fails to load
                        const target = e.target as HTMLImageElement
                        target.style.display = 'none'
                        const parent = target.parentElement
                        if (parent) {
                          parent.innerHTML = msg.roleName === 'Alice' ? '⚡' 
                            : msg.roleName === 'Bob' ? '🧠' 
                            : msg.roleName === 'Charlie' ? '🔥' 
                            : '⭐' // Kirby emoji (星之卡比) for default assistant
                          parent.className += ' text-3xl'
                        }
                      }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {msg.type === 'thinking' && <Brain className="w-4 h-4 text-blue-500 animate-pulse" />}
                      {msg.type === 'working' && <Loader2 className="w-4 h-4 text-primary animate-spin" />}
                      {msg.type === 'complete' && <span className="text-green-500 text-lg">✓</span>}
                      <p className="text-sm font-semibold">
                        {roleDisplayName}
                        {msg.type === 'thinking' && ' (Thinking...)'}
                        {msg.type === 'working' && ' (Working...)'}
                      </p>
                    </div>
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    {msg.type === 'complete' && (
                      <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                        <span>✅</span>
                        <span>Completed</span>
                  </p>
                )}
                  </div>
                </div>
              </div>
            )
          })}
          {messages.length === 0 && currentTask && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4 animate-fade-in">
              <div className="text-4xl animate-bounce">🚀</div>
              <div className="text-sm text-pink-600 dark:text-pink-400 text-center font-medium">
                Project is starting...
              </div>
              <div className="text-xs text-pink-500 dark:text-pink-500 text-center">
                Your team is preparing to work
              </div>
              </div>
            )}
          <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        
        {/* Scroll to bottom button */}
        {showScrollToBottom && (
          <button
            onClick={scrollToBottom}
            className="absolute bottom-20 right-6 z-10 p-2 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white shadow-lg pokemon-glow transition-all transform hover:scale-110 animate-float"
            aria-label="Scroll to bottom"
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="flex-shrink-0 p-4 border-t border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-50/50 to-purple-50/50 dark:from-pink-950/50 dark:to-purple-950/50 space-y-3">
        <Textarea
          placeholder="Describe your project idea... (e.g., Create a 2048 game)"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          disabled={isGenerating}
          className="min-h-[100px] resize-none border-pink-300 dark:border-pink-600 bg-white/80 dark:bg-purple-950/80 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700 rounded-xl"
        />
        
        <div className="flex items-center gap-2">
          <label className="text-sm text-pink-700 dark:text-pink-300 font-medium">Budget:</label>
          <input
            type="number"
            value={investment}
            onChange={(e) => setInvestment(parseFloat(e.target.value))}
            disabled={isGenerating}
            min="1"
            max="50"
            step="0.5"
            className="w-20 px-2 py-1 text-sm border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
          />
          <span className="text-sm text-pink-600 dark:text-pink-400">USD</span>
        </div>
        
        <Button
          type="submit"
          disabled={!idea.trim() || isGenerating}
          className="w-full gap-2 pokemon-gradient hover:pokemon-glow text-white font-semibold rounded-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Generate Project
            </>
          )}
        </Button>
      </form>
    </div>
  )
}