import { CheckCircle2, Circle, Loader2, Brain, FileText, Code } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { Progress } from './ui/progress'
import { ScrollArea } from './ui/scroll-area'

const stages = [
  { id: 'pm', name: 'Product Manager', description: 'Writing PRD', icon: FileText },
  { id: 'arch', name: 'Architect', description: 'Designing system', icon: FileText },
  { id: 'eng', name: 'Engineer', description: 'Implementing code', icon: Code },
]

export function ProgressPanel() {
  const { currentTask } = useTask()

  const getCurrentStageIndex = () => {
    if (!currentTask) return -1
    const stage = currentTask.current_stage.toLowerCase()
    if (stage.includes('product') || stage.includes('prd')) return 0
    if (stage.includes('architect') || stage.includes('design')) return 1
    if (stage.includes('engineer') || stage.includes('code')) return 2
    return -1
  }

  const getStageStatus = (stageId: string) => {
    if (!currentTask) return 'pending'
    const stage = currentTask.current_stage.toLowerCase()
    const role = currentTask.current_stage.split(':')[0]?.toLowerCase() || ''
    
    if (stageId === 'pm') {
      if (role.includes('product') || stage.includes('prd')) {
        if (stage.includes('thinking')) return 'thinking'
        if (stage.includes('starting')) return 'starting'
        if (stage.includes('executing')) return 'executing'
        if (stage.includes('completed') || stage.includes('complete')) return 'completed'
        return 'active'
      }
      if (getCurrentStageIndex() > 0) return 'completed'
    } else if (stageId === 'arch') {
      if (role.includes('architect') || stage.includes('design')) {
        if (stage.includes('thinking')) return 'thinking'
        if (stage.includes('starting')) return 'starting'
        if (stage.includes('executing')) return 'executing'
        if (stage.includes('completed') || stage.includes('complete')) return 'completed'
        return 'active'
      }
      if (getCurrentStageIndex() > 1) return 'completed'
      if (getCurrentStageIndex() === 1) return 'active'
    } else if (stageId === 'eng') {
      if (role.includes('engineer') || stage.includes('code')) {
        if (stage.includes('thinking')) return 'thinking'
        if (stage.includes('starting')) return 'starting'
        if (stage.includes('executing')) return 'executing'
        if (stage.includes('completed') || stage.includes('complete')) return 'completed'
        return 'active'
      }
      if (getCurrentStageIndex() === 2) return 'active'
    }
    
    return 'pending'
  }

  const currentStageIndex = getCurrentStageIndex()

  return (
    <div className="flex-1 flex flex-col bg-background min-h-0">
      <div className="flex-shrink-0 p-6 border-b border-border">
        <h2 className="font-semibold text-lg mb-4">Generation Progress</h2>
        
        {currentTask ? (
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-muted-foreground">Overall Progress</span>
                <span className="font-medium">{currentTask.progress}%</span>
              </div>
              <Progress value={currentTask.progress} className="h-2" />
            </div>
            
            <div className="text-sm">
              <span className="text-muted-foreground">Status: </span>
              <span className="font-medium capitalize">{currentTask.status}</span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Enter your project idea to start generation
          </p>
        )}
      </div>
      
      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full p-6">
        <div className="space-y-6">
          {stages.map((stage, index) => {
            const status = getStageStatus(stage.id)
            const StageIcon = stage.icon
            const isCompleted = status === 'completed'
            const isActive = status === 'active' || status === 'thinking' || status === 'starting' || status === 'executing'
            const isPending = status === 'pending'
            const isThinking = status === 'thinking'
            const isStarting = status === 'starting'
            const isExecuting = status === 'executing'
            
            return (
              <div key={stage.id} className="flex gap-4">
                <div className="flex flex-col items-center">
                  {isCompleted && (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  )}
                  {isThinking && (
                    <Brain className="w-6 h-6 text-blue-500 animate-pulse" />
                  )}
                  {(isStarting || isExecuting) && (
                    <Loader2 className="w-6 h-6 text-primary animate-spin" />
                  )}
                  {isPending && (
                    <Circle className="w-6 h-6 text-muted-foreground" />
                  )}
                  {index < stages.length - 1 && (
                    <div
                      className={`w-0.5 h-16 mt-2 ${
                        isCompleted ? 'bg-green-500' : isActive ? 'bg-primary/30' : 'bg-border'
                      }`}
                    />
                  )}
                </div>
                
                <div className="flex-1 pb-8">
                  <div className="flex items-center gap-2 mb-1">
                    <StageIcon className={`w-4 h-4 ${
                      isActive ? 'text-primary' : isPending ? 'text-muted-foreground' : 'text-green-500'
                    }`} />
                    <h3 className={`font-medium ${
                      isActive ? 'text-primary' : isPending ? 'text-muted-foreground' : ''
                    }`}>
                      {stage.name}
                    </h3>
                  </div>
                  
                  {isPending && (
                    <p className="text-sm text-muted-foreground">
                      {stage.description}
                    </p>
                  )}
                  
                  {isThinking && currentTask && (
                    <div className="mt-2 space-y-2">
                      <div className="p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md">
                        <p className="text-sm font-medium text-blue-900 dark:text-blue-100 flex items-center gap-2">
                          <Brain className="w-4 h-4" />
                          Thinking...
                        </p>
                        <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                          {currentTask.current_stage}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {isStarting && currentTask && (
                    <div className="mt-2 space-y-2">
                      <div className="p-3 bg-primary/10 border border-primary/20 rounded-md">
                        <p className="text-sm font-medium text-primary flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Starting...
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {currentTask.current_stage}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {isExecuting && currentTask && (
                    <div className="mt-2 space-y-2">
                      <div className="p-3 bg-primary/10 border border-primary/20 rounded-md">
                        <p className="text-sm font-medium text-primary flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Working...
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {currentTask.current_stage}
                        </p>
                        {currentTask.message && (
                          <p className="text-xs text-muted-foreground mt-2 italic">
                            {currentTask.message}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {isActive && !isThinking && !isStarting && !isExecuting && currentTask && (
                    <div className="mt-2 p-3 bg-secondary rounded-md">
                      <p className="text-sm">{currentTask.current_stage}</p>
                    </div>
                  )}
                  
                  {isCompleted && (
                    <div className="mt-2 p-2 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-md">
                      <p className="text-sm text-green-700 dark:text-green-300 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" />
                        Completed
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
        
        {currentTask?.status === 'completed' && currentTask.result && (
          <div className="mt-8 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
            <h3 className="font-medium text-green-900 dark:text-green-100 mb-2">
              🎉 Project Generated Successfully!
            </h3>
            <div className="text-sm space-y-1 text-green-800 dark:text-green-200">
              <p>Files: {currentTask.result.files.length} source files</p>
              <p>Docs: {currentTask.result.docs.length} documents</p>
              <p>Tokens: {currentTask.result.tokens.toLocaleString()}</p>
            </div>
          </div>
        )}
        </ScrollArea>
      </div>
    </div>
  )
}