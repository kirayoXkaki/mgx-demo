import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { ScrollArea } from './ui/scroll-area'

export function ChatPanel() {
  const [idea, setIdea] = useState('')
  const [investment, setInvestment] = useState(5.0)
  const { currentTask, isGenerating, startGeneration } = useTask()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!idea.trim() || isGenerating) return
    
    await startGeneration(idea, investment)
  }

  return (
    <div className="w-80 border-r border-border flex flex-col bg-card">
      <div className="p-4 border-b border-border">
        <h2 className="font-semibold text-lg">Chat</h2>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        {currentTask && (
          <div className="space-y-4">
            <div className="bg-primary/10 rounded-lg p-3">
              <p className="text-sm font-medium mb-1">You</p>
              <p className="text-sm">{currentTask.idea}</p>
            </div>
            
            {currentTask.status !== 'pending' && (
              <div className="bg-secondary rounded-lg p-3">
                <p className="text-sm font-medium mb-1">MGX Assistant</p>
                <p className="text-sm">{currentTask.current_stage}</p>
                {currentTask.status === 'completed' && (
                  <p className="text-xs text-muted-foreground mt-2">
                    ✅ Project generated successfully!
                  </p>
                )}
                {currentTask.status === 'failed' && (
                  <p className="text-xs text-destructive mt-2">
                    ❌ {currentTask.error}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </ScrollArea>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-border space-y-3">
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