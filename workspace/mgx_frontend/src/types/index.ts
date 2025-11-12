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
  message?: string
  role?: string
  action?: string
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
  type: 'status' | 'progress' | 'complete' | 'error' | 'thinking' | 'action_start' | 'action_executing' | 'action_complete' | 'saving' | 'stream_chunk' | 'file_update' | 'file_content' | 'file_complete' | 'chat_message'
  status?: string
  stage?: string
  progress?: number
  message?: string
  role?: string
  action?: string
  result?: TaskResult
  error?: string
  chunk?: string
  accumulated?: string
  filepath?: string
  content?: string
  file_action?: string
}