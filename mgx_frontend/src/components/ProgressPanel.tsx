import { CheckCircle2, Circle, Loader2 } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { Progress } from './ui/progress'
import { ScrollArea } from './ui/scroll-area'

const stages = [
  { id: 'pm', name: 'Product Manager', description: 'Writing PRD' },
  { id: 'arch', name: 'Architect', description: 'Designing system' },
  { id: 'eng', name: 'Engineer', description: 'Implementing code' },
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

  const currentStageIndex = getCurrentStageIndex()

  return (
    <div className="flex-1 flex flex-col bg-background">
      <div className="p-6 border-b border-border">
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
      
      <ScrollArea className="flex-1 p-6">
        <div className="space-y-6">
          {stages.map((stage, index) => {
            const isCompleted = currentTask && currentStageIndex > index
            const isActive = currentTask && currentStageIndex === index
            const isPending = !currentTask || currentStageIndex < index
            
            return (
              <div key={stage.id} className="flex gap-4">
                <div className="flex flex-col items-center">
                  {isCompleted && (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  )}
                  {isActive && (
                    <Loader2 className="w-6 h-6 text-primary animate-spin" />
                  )}
                  {isPending && (
                    <Circle className="w-6 h-6 text-muted-foreground" />
                  )}
                  {index < stages.length - 1 && (
                    <div
                      className={`w-0.5 h-16 mt-2 ${
                        isCompleted ? 'bg-green-500' : 'bg-border'
                      }`}
                    />
                  )}
                </div>
                
                <div className="flex-1 pb-8">
                  <h3 className={`font-medium mb-1 ${
                    isActive ? 'text-primary' : isPending ? 'text-muted-foreground' : ''
                  }`}>
                    {stage.name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {stage.description}
                  </p>
                  {isActive && currentTask && (
                    <div className="mt-2 p-3 bg-secondary rounded-md">
                      <p className="text-sm">{currentTask.current_stage}</p>
                    </div>
                  )}
                  {isCompleted && (
                    <p className="text-sm text-green-600 mt-2">✓ Completed</p>
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
  )
}