import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { Task, FileItem, ProgressUpdate } from '../types'

interface TaskContextType {
  currentTask: Task | null
  files: FileItem[]
  isGenerating: boolean
  streamingFiles: Map<string, string> // filepath -> content (for real-time updates)
  chatMessages: Array<{id: string, role: string, content: string, timestamp: Date}> // Direct chat messages queue
  startGeneration: (idea: string, investment: number) => Promise<void>
  fetchFiles: () => Promise<void>
  loadProjectFiles: (taskId: string) => Promise<void>
  downloadProject: () => Promise<void>
  clearFiles: () => void
}

const TaskContext = createContext<TaskContextType | undefined>(undefined)

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [currentTask, setCurrentTask] = useState<Task | null>(null)
  const [files, setFiles] = useState<FileItem[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [streamingFiles, setStreamingFiles] = useState<Map<string, string>>(new Map())
  const [chatMessages, setChatMessages] = useState<Array<{id: string, role: string, content: string, timestamp: Date}>>([])

  const startGeneration = useCallback(async (idea: string, investment: number) => {
    setIsGenerating(true)
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, investment, n_round: 5 }),
      })
      
      const data = await response.json()
      const taskId = data.task_id
      
      // Clear previous task data when starting new generation
      setChatMessages([])
      setStreamingFiles(new Map())
      setFiles([])
      
      // Initialize task
      setCurrentTask({
        task_id: taskId,
        status: 'pending',
        progress: 0,
        current_stage: 'Initializing',
        cost: 0,
        idea,
        investment,
        n_round: 5,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      
      // Connect WebSocket (use relative path to go through vite proxy)
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/ws/${taskId}`
      const websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        console.log('WebSocket connected:', taskId)
      }
      
      websocket.onmessage = (event) => {
        try {
        const update: ProgressUpdate = JSON.parse(event.data)
        
        // Debug: Log chat_message type updates
        if (update.type === 'chat_message') {
          console.log('💬 [Frontend] chat_message received:', {
            role: update.role,
            message: update.message?.substring(0, 100),
            stage: update.stage
          })
          
          // IMPORTANT: Immediately add chat_message to queue, don't wait for currentTask update
          if (update.message && update.role) {
            console.log('💬 [Frontend] Processing chat_message, message:', update.message.substring(0, 50), 'role:', update.role)
            setChatMessages(prev => {
              console.log('💬 [Frontend] Current chatMessages queue length:', prev.length)
              // Check if this exact message already exists
              const exists = prev.some(msg => 
                msg.role === update.role && 
                msg.content === update.message
              )
              if (!exists) {
                const newChatMsg = {
                  id: `chat-${Date.now()}-${Math.random()}`,
                  role: update.role!,
                  content: update.message!,
                  timestamp: new Date()
                }
                console.log('💬 [Frontend] Adding chat_message to queue immediately:', newChatMsg)
                return [...prev, newChatMsg]
              } else {
                console.log('💬 [Frontend] Chat message already exists in queue, skipping')
              }
              return prev
            })
          } else {
            console.log('💬 [Frontend] chat_message missing message or role:', {hasMessage: !!update.message, hasRole: !!update.role})
          }
        }
        
        setCurrentTask((prev) => {
          if (!prev) return null
          
          return {
            ...prev,
            status: update.status || prev.status,
              progress: update.progress !== undefined ? update.progress : prev.progress,
            current_stage: update.stage || prev.current_stage,
            result: update.result || prev.result,
            error: update.error || prev.error,
              // IMPORTANT: For chat_message type, always use the new message (don't fallback to prev)
              message: (update.type === 'chat_message' && update.message) ? update.message : (update.message || prev.message),
              role: update.role || prev.role,
              action: update.action || prev.action,
              // Update cost if provided in update
              cost: update.cost !== undefined ? update.cost : prev.cost,
            updated_at: new Date().toISOString(),
          }
        })
          
          // Handle file updates for real-time code/document display
          if (update.type === 'file_update' && update.filepath) {
            console.log('📝 [Frontend] file_update received:', update.filepath)
            setStreamingFiles(prev => {
              const newMap = new Map(prev)
              if (!newMap.has(update.filepath!)) {
                newMap.set(update.filepath!, '')
                console.log('📝 [Frontend] Added to streamingFiles:', update.filepath)
              }
              return newMap
            })
            // Auto-select the new file
            if (update.filepath) {
              // Trigger file selection in FileExplorer
              setTimeout(() => {
                const event = new CustomEvent('fileSelected', { detail: { filepath: update.filepath } })
                window.dispatchEvent(event)
              }, 100)
            }
          } else if (update.type === 'file_content' && update.filepath && update.content !== undefined) {
            console.log('📝 [Frontend] file_content received:', update.filepath, 'length:', update.content?.length)
            setStreamingFiles(prev => {
              const newMap = new Map(prev)
              newMap.set(update.filepath!, update.content!)
              console.log('📝 [Frontend] Updated streamingFiles, now has', newMap.size, 'files')
              return newMap
            })
          } else if (update.type === 'file_complete' && update.filepath && update.content !== undefined) {
            // Remove from streamingFiles since file is complete
            setStreamingFiles(prev => {
              const newMap = new Map(prev)
              newMap.delete(update.filepath!) // Remove from streaming files
              return newMap
            })
            // Add to files list
            setFiles(prev => {
              const exists = prev.find(f => f.path === update.filepath)
              if (!exists) {
                return [...prev, {
                  path: update.filepath!,
                  content: update.content!,
                  type: update.filepath!.includes('src/') || update.filepath!.endsWith('.js') || update.filepath!.endsWith('.ts') || update.filepath!.endsWith('.py') || update.filepath!.endsWith('.jsx') || update.filepath!.endsWith('.tsx') || update.filepath!.endsWith('.html') || update.filepath!.endsWith('.css') || update.filepath!.endsWith('.json') ? 'source' : 'document'
                }]
              }
              return prev.map(f => 
                f.path === update.filepath 
                  ? { ...f, content: update.content! }
                  : f
              )
            })
          }
          
          // Handle stream chunks for chat display - only show action status, not file content
          if (update.type === 'stream_chunk' && update.role && update.action) {
            // Update task message with action description, not file content
            const actionMessages: Record<string, string> = {
              'WritePRD': 'Writing Product Requirements Document...',
              'WriteDesign': 'Designing system architecture...',
              'WriteCode': 'Generating code files...'
            }
            setCurrentTask(prev => {
              if (!prev) return null
              return {
                ...prev,
                message: actionMessages[update.action || ''] || `${update.role} is working...`,
                role: update.role || prev.role,
                action: update.action || prev.action
              }
            })
          }
          
          // Handle action completion - clear streaming files for that action
          if (update.type === 'action_complete' && update.role) {
            // When an action completes, clear all streaming files for that role
            // This ensures "Writing..." indicators are removed
            setStreamingFiles(prev => {
              const newMap = new Map(prev)
              // Keep only files that are still being written by other roles
              // For now, clear all since we can't easily determine which files belong to which role
              // The file_complete messages should have already cleared individual files
              return newMap
            })
          }
        
        if (update.type === 'complete') {
          setIsGenerating(false)
            setStreamingFiles(new Map()) // Clear all streaming files when task completes
            // DON'T clear chatMessages here - keep them so users can see the conversation history
          fetchFiles()
        } else if (update.type === 'error') {
          setIsGenerating(false)
            setStreamingFiles(new Map())
            // DON'T clear chatMessages on error - keep them for debugging/context
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsGenerating(false)
      }
      
      websocket.onclose = () => {
        console.log('WebSocket closed')
      }
      
      setWs(websocket)
      
    } catch (error) {
      console.error('Failed to start generation:', error)
      setIsGenerating(false)
      setCurrentTask((prev) => {
        if (!prev) return null
        return {
          ...prev,
          status: 'failed',
          error: error instanceof Error ? error.message : 'Failed to start generation'
        }
      })
    }
  }, [])

  const fetchFiles = useCallback(async () => {
    if (!currentTask?.task_id) return
    
    try {
      const response = await fetch(`/api/files/${currentTask.task_id}`)
      const data = await response.json()
      setFiles(data.files)
    } catch (error) {
      console.error('Failed to fetch files:', error)
    }
  }, [currentTask?.task_id])

  const loadProjectFiles = useCallback(async (taskId: string) => {
    try {
      console.log('📁 [Task] Loading project files for task:', taskId)
      const response = await fetch(`/api/files/${taskId}`)
      if (!response.ok) {
        if (response.status === 404) {
          console.log('📁 [Task] Project files not found for task:', taskId)
          return
        }
        throw new Error(`Failed to load project files: ${response.status}`)
      }
      const data = await response.json()
      setFiles(data.files || [])
      console.log('✅ [Task] Loaded project files:', data.files?.length || 0, 'files')
      
      // Also set the task as completed if we're loading from history
      setCurrentTask(prev => {
        if (prev?.task_id === taskId) {
          return prev
        }
        return {
          task_id: taskId,
          status: 'completed',
          progress: 100,
          current_stage: 'Loaded from history',
          cost: 0,
          idea: '',
          investment: 0,
          n_round: 5,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      })
    } catch (error) {
      console.error('❌ [Task] Failed to load project files:', error)
    }
  }, [])

  const downloadProject = useCallback(async () => {
    if (!currentTask?.task_id) return
    
    window.open(`/api/download/${currentTask.task_id}`, '_blank')
  }, [currentTask?.task_id])

  const clearFiles = useCallback(() => {
    setFiles([])
    setStreamingFiles(new Map())
    setCurrentTask(null)
    setChatMessages([])
    // Close WebSocket if open
    if (ws) {
      ws.close()
      setWs(null)
    }
    console.log('🧹 [Task] Cleared all files and task state')
  }, [ws])

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [ws])

  return (
    <TaskContext.Provider
      value={{
        currentTask,
        files,
        isGenerating,
        streamingFiles,
        chatMessages,
        startGeneration,
        fetchFiles,
        loadProjectFiles,
        downloadProject,
        clearFiles,
      }}
    >
      {children}
    </TaskContext.Provider>
  )
}

export function useTask() {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTask must be used within TaskProvider')
  }
  return context
}