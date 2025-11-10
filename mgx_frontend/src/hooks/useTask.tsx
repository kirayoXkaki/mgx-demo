import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { Task, FileItem, ProgressUpdate } from '../types'

interface TaskContextType {
  currentTask: Task | null
  files: FileItem[]
  isGenerating: boolean
  startGeneration: (idea: string, investment: number) => Promise<void>
  fetchFiles: () => Promise<void>
  downloadProject: () => Promise<void>
}

const TaskContext = createContext<TaskContextType | undefined>(undefined)

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [currentTask, setCurrentTask] = useState<Task | null>(null)
  const [files, setFiles] = useState<FileItem[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)

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
      
      // Connect WebSocket
      const websocket = new WebSocket(`ws://localhost:8000/api/ws/${taskId}`)
      
      websocket.onmessage = (event) => {
        const update: ProgressUpdate = JSON.parse(event.data)
        
        setCurrentTask((prev) => {
          if (!prev) return null
          
          return {
            ...prev,
            status: update.status || prev.status,
            progress: update.progress || prev.progress,
            current_stage: update.stage || prev.current_stage,
            result: update.result || prev.result,
            error: update.error || prev.error,
            updated_at: new Date().toISOString(),
          }
        })
        
        if (update.type === 'complete') {
          setIsGenerating(false)
          fetchFiles()
        } else if (update.type === 'error') {
          setIsGenerating(false)
        }
      }
      
      websocket.onerror = () => {
        setIsGenerating(false)
      }
      
      setWs(websocket)
      
    } catch (error) {
      console.error('Failed to start generation:', error)
      setIsGenerating(false)
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

  const downloadProject = useCallback(async () => {
    if (!currentTask?.task_id) return
    
    window.open(`/api/download/${currentTask.task_id}`, '_blank')
  }, [currentTask?.task_id])

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
        startGeneration,
        fetchFiles,
        downloadProject,
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