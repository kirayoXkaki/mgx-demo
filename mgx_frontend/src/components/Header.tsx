import { Rocket, DollarSign, Download } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { formatCost } from '../lib/utils'
import { Button } from './ui/button'

export function Header() {
  const { currentTask, downloadProject } = useTask()

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <Rocket className="w-6 h-6 text-primary" />
        <h1 className="text-xl font-bold">MGX Demo</h1>
        <span className="text-sm text-muted-foreground">AI Software Development Platform</span>
      </div>
      
      <div className="flex items-center gap-4">
        {currentTask && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-secondary">
            <DollarSign className="w-4 h-4" />
            <span className="text-sm font-medium">
              Cost: {formatCost(currentTask.cost)}
            </span>
          </div>
        )}
        
        {currentTask?.status === 'completed' && (
          <Button onClick={downloadProject} size="sm" className="gap-2">
            <Download className="w-4 h-4" />
            Download Project
          </Button>
        )}
      </div>
    </header>
  )
}