export interface Task {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  current_stage: string
  cost: number
  idea: string
  investment: number
  n_round: number
  result?: TaskResult
  error?: string
  created_at: string
  updated_at: string
}

export interface TaskResult {
  project_path: string
  files: string[]
  docs: string[]
  cost: number
  tokens: number
}

export interface FileItem {
  path: string
  content: string
  type: 'source' | 'document'
}

export interface ProgressUpdate {
  type: 'status' | 'progress' | 'complete' | 'error'
  status?: string
  stage?: string
  progress?: number
  message?: string
  result?: TaskResult
  error?: string
}