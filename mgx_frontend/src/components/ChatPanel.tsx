import { useState, useEffect, useRef } from 'react'
import { Send, Loader2, Brain, FileText, Code } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { ScrollArea } from './ui/scroll-area'

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
  const { currentTask, isGenerating, startGeneration } = useTask()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  // Update messages based on task updates
  useEffect(() => {
    if (!currentTask) {
      setMessages([])
      return
    }
    
    // Add user message
    if (currentTask.idea) {
      setMessages(prev => {
        const hasUserMsg = prev.some(msg => msg.role === 'user' && msg.content === currentTask.idea)
        if (!hasUserMsg) {
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
    if (currentTask.message || currentTask.current_stage) {
        const newContent = currentTask.message || currentTask.current_stage
        
        // Determine message type
        let type: 'thinking' | 'working' | 'message' | 'complete' = 'message'
        if (currentTask.current_stage?.toLowerCase().includes('thinking')) {
          type = 'thinking'
        } else if (currentTask.current_stage?.toLowerCase().includes('executing') || 
                   currentTask.current_stage?.toLowerCase().includes('working') ||
                   currentTask.current_stage?.toLowerCase().includes('starting')) {
          type = 'working'
        } else if (currentTask.status === 'completed') {
          type = 'complete'
        }
        
        // Find existing message for this role (allow updating working messages)
        const existingMsgIndex = messages.findIndex(msg => 
          msg.role === 'assistant' && 
          msg.roleName === currentTask.role &&
          (type === 'working' || msg.type === type)
        )
        
        if (existingMsgIndex >= 0) {
          // Update existing message (append for working type to show progress)
          setMessages(prev => prev.map((msg, idx) => {
            if (idx === existingMsgIndex) {
              // For working messages, show accumulated content if available
              if (type === 'working' && currentTask.message && msg.content !== newContent) {
                return { ...msg, content: newContent, type }
              }
              return { ...msg, content: newContent, type }
            }
            return msg
          }))
        } else {
          // Add new message
          setMessages(prev => [...prev, {
            id: `assistant-${Date.now()}-${Math.random()}`,
            role: 'assistant',
            roleName: currentTask.role,
            content: newContent,
            type,
            timestamp: new Date()
          }])
        }
      }
  }, [currentTask])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!idea.trim() || isGenerating) return
    
    await startGeneration(idea, investment)
  }

  return (
    <div className="w-80 border-r border-border flex flex-col bg-card min-h-0">
      <div className="flex-shrink-0 p-4 border-b border-border">
        <h2 className="font-semibold text-lg">Chat</h2>
      </div>
      
      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full p-4">
        <div className="space-y-4">
          {messages.map((msg) => {
            const getRoleIcon = () => {
              if (msg.roleName === 'ProductManager') return <FileText className="w-4 h-4" />
              if (msg.roleName === 'Architect') return <FileText className="w-4 h-4" />
              if (msg.roleName === 'Engineer') return <Code className="w-4 h-4" />
              return null
            }
            
            const getRoleColor = () => {
              if (msg.roleName === 'ProductManager') return 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800'
              if (msg.roleName === 'Architect') return 'bg-purple-50 dark:bg-purple-950 border-purple-200 dark:border-purple-800'
              if (msg.roleName === 'Engineer') return 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'
              return 'bg-secondary'
            }
            
            if (msg.role === 'user') {
              return (
                <div key={msg.id} className="bg-primary/10 rounded-lg p-3">
                  <p className="text-sm font-medium mb-1">You</p>
                  <p className="text-sm">{msg.content}</p>
                </div>
              )
            }
            
            return (
              <div key={msg.id} className={`rounded-lg p-3 border ${getRoleColor()}`}>
                <div className="flex items-center gap-2 mb-1">
                  {msg.type === 'thinking' && <Brain className="w-4 h-4 text-blue-500 animate-pulse" />}
                  {msg.type === 'working' && <Loader2 className="w-4 h-4 text-primary animate-spin" />}
                  {msg.type === 'complete' && <span className="text-green-500">✓</span>}
                  {getRoleIcon()}
                  <p className="text-sm font-medium">
                    {msg.roleName || 'MGX Assistant'}
                    {msg.type === 'thinking' && ' (Thinking...)'}
                    {msg.type === 'working' && ' (Working...)'}
                  </p>
                </div>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.type === 'complete' && (
                  <p className="text-xs text-muted-foreground mt-2">
                    ✅ Completed
                  </p>
                )}
              </div>
            )
          })}
          {messages.length === 0 && currentTask && (
            <div className="text-sm text-muted-foreground text-center py-8">
              Enter your project idea to start
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        </ScrollArea>
      </div>
      
      <form onSubmit={handleSubmit} className="flex-shrink-0 p-4 border-t border-border space-y-3">
        <Textarea
          placeholder="Describe your project idea... (e.g., Create a 2048 game)"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          disabled={isGenerating}
          className="min-h-[100px] resize-none"
        />
        
        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Budget:</label>
          <input
            type="number"
            value={investment}
            onChange={(e) => setInvestment(parseFloat(e.target.value))}
            disabled={isGenerating}
            min="1"
            max="50"
            step="0.5"
            className="w-20 px-2 py-1 text-sm border border-input rounded-md bg-background"
          />
          <span className="text-sm text-muted-foreground">USD</span>
        </div>
        
        <Button
          type="submit"
          disabled={!idea.trim() || isGenerating}
          className="w-full gap-2"
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