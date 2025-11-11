import { useState, useEffect, useMemo } from 'react'
import { File, Folder, FolderOpen, ChevronRight, ChevronDown, Loader2, CheckCircle2, Circle, Brain, FileText, Code, Activity } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { ScrollArea } from './ui/scroll-area'
import { Progress } from './ui/progress'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface FileTreeNode {
  name: string
  path: string
  type: 'file' | 'folder'
  children?: FileTreeNode[]
  isStreaming?: boolean
}

const stages = [
  { id: 'pm', name: 'Product Manager', description: 'Writing PRD', icon: FileText },
  { id: 'arch', name: 'Architect', description: 'Designing system', icon: FileText },
  { id: 'eng', name: 'Engineer', description: 'Implementing code', icon: Code },
]

export function FileEditor() {
  const { files, streamingFiles, currentTask } = useTask()
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [showProgress, setShowProgress] = useState(true)

  // Auto-select first streaming file
  useEffect(() => {
    if (streamingFiles.size > 0) {
      const streamingFileList = Array.from(streamingFiles.keys())
      if (!selectedFile || !streamingFiles.has(selectedFile)) {
        const latestFile = streamingFileList[streamingFileList.length - 1]
        setSelectedFile(latestFile)
        // Auto-expand folder containing the file
        const folderPath = latestFile.split('/').slice(0, -1).join('/')
        if (folderPath) {
          setExpandedFolders(prev => new Set([...prev, folderPath]))
        }
      }
    }
    
    // Listen for file selection events
    const handleFileSelected = (event: CustomEvent) => {
      if (event.detail?.filepath) {
        setSelectedFile(event.detail.filepath)
        const folderPath = event.detail.filepath.split('/').slice(0, -1).join('/')
        if (folderPath) {
          setExpandedFolders(prev => new Set([...prev, folderPath]))
        }
      }
    }
    
    window.addEventListener('fileSelected', handleFileSelected as EventListener)
    return () => {
      window.removeEventListener('fileSelected', handleFileSelected as EventListener)
    }
  }, [streamingFiles, selectedFile])

  // Build file tree structure
  const fileTree = useMemo(() => {
    const allFiles = [
      ...files,
      ...Array.from(streamingFiles.entries())
        .filter(([path]) => !files.find(f => f.path === path))
        .map(([path, content]) => ({
          path,
          content,
          type: (path.includes('src/') || path.endsWith('.js') || path.endsWith('.ts') || path.endsWith('.py') || path.endsWith('.jsx') || path.endsWith('.tsx')) ? 'source' : 'document' as const
        }))
    ]

    if (allFiles.length === 0) return []

    const tree: FileTreeNode[] = []
    const pathMap = new Map<string, FileTreeNode>()

    allFiles.forEach(file => {
      const parts = file.path.split('/').filter(p => p) // Remove empty parts
      let currentPath = ''
      
      parts.forEach((part, index) => {
        const isLast = index === parts.length - 1
        const path = currentPath ? `${currentPath}/${part}` : part
        
        if (!pathMap.has(path)) {
          const node: FileTreeNode = {
            name: part,
            path: path,
            type: isLast ? 'file' : 'folder',
            children: isLast ? undefined : [],
            isStreaming: isLast ? streamingFiles.has(file.path) : false
          }
          pathMap.set(path, node)
          
          if (currentPath === '') {
            tree.push(node)
          } else {
            const parent = pathMap.get(currentPath)
            if (parent && parent.children) {
              parent.children.push(node)
            }
          }
        } else if (isLast) {
          const node = pathMap.get(path)!
          node.isStreaming = streamingFiles.has(file.path)
        }
        
        currentPath = path
      })
    })

    // Sort tree: folders first, then files, both alphabetically
    const sortTree = (nodes: FileTreeNode[]): FileTreeNode[] => {
      return nodes.sort((a, b) => {
        if (a.type !== b.type) {
          return a.type === 'folder' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      }).map(node => ({
        ...node,
        children: node.children ? sortTree(node.children) : undefined
      }))
    }

    return sortTree(tree)
  }, [files, streamingFiles])

  // Auto-expand folders that contain streaming files
  useEffect(() => {
    const foldersToExpand = new Set<string>()
    const hasStreaming = (node: FileTreeNode): boolean => {
      if (node.isStreaming) return true
      if (node.children) {
        return node.children.some(child => hasStreaming(child))
      }
      return false
    }
    
    fileTree.forEach(node => {
      if (hasStreaming(node)) {
        foldersToExpand.add(node.path)
      }
    })
    
    if (foldersToExpand.size > 0) {
      setExpandedFolders(prev => new Set([...prev, ...foldersToExpand]))
    }
  }, [fileTree])

  // Get file content
  const getFileContent = (filepath: string) => {
    if (streamingFiles.has(filepath)) {
      return streamingFiles.get(filepath) || ''
    }
    const file = files.find(f => f.path === filepath)
    return file?.content || ''
  }

  const selectedFileContent = selectedFile ? {
    path: selectedFile,
    content: getFileContent(selectedFile),
    type: selectedFile.includes('src/') || selectedFile.endsWith('.js') || selectedFile.endsWith('.ts') || selectedFile.endsWith('.py') || selectedFile.endsWith('.jsx') || selectedFile.endsWith('.tsx') ? 'source' : 'document' as const
  } : null

  // Get file extension for syntax highlighting
  const getLanguage = (filepath: string): string => {
    const ext = filepath.split('.').pop()?.toLowerCase()
    const langMap: Record<string, string> = {
      'js': 'javascript',
      'jsx': 'jsx',
      'ts': 'typescript',
      'tsx': 'tsx',
      'py': 'python',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
    }
    return langMap[ext || ''] || 'text'
  }

  // Toggle folder expansion
  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev)
      if (newSet.has(path)) {
        newSet.delete(path)
      } else {
        newSet.add(path)
      }
      return newSet
    })
  }

  // Render file tree node
  const renderTreeNode = (node: FileTreeNode, level: number = 0) => {
    const isExpanded = expandedFolders.has(node.path)
    const isSelected = selectedFile === node.path
    const hasStreamingChild = node.children?.some(child => child.isStreaming || streamingFiles.has(child.path))

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <button
            onClick={() => toggleFolder(node.path)}
            className={`w-full flex items-center gap-1 py-1 px-2 text-sm rounded hover:bg-accent ${
              isSelected ? 'bg-accent' : ''
            }`}
            style={{ paddingLeft: `${8 + level * 16}px` }}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-3 h-3 text-muted-foreground" />
            )}
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 text-yellow-500" />
            ) : (
              <Folder className="w-4 h-4 text-yellow-500" />
            )}
            <span className="flex-1 text-left truncate">{node.name}</span>
            {(node.isStreaming || hasStreamingChild) && (
              <Loader2 className="w-3 h-3 text-primary animate-spin" />
            )}
          </button>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderTreeNode(child, level + 1))}
            </div>
          )}
        </div>
      )
    } else {
      const isStreaming = streamingFiles.has(node.path)
      return (
        <button
          key={node.path}
          onClick={() => setSelectedFile(node.path)}
          className={`w-full flex items-center gap-2 py-1 px-2 text-sm rounded hover:bg-accent ${
            isSelected ? 'bg-accent border-l-2 border-primary' : ''
          } ${isStreaming ? 'border-l-2 border-primary' : ''}`}
          style={{ paddingLeft: `${8 + level * 16}px` }}
        >
          <File className="w-4 h-4 text-muted-foreground" />
          <span className="flex-1 text-left truncate">{node.name}</span>
          {isStreaming && (
            <>
              <Loader2 className="w-3 h-3 text-primary animate-spin" />
              <span className="text-xs text-primary">Writing...</span>
            </>
          )}
        </button>
      )
    }
  }

  // Get stage status for progress
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
      return 'completed'
    } else if (stageId === 'arch') {
      if (role.includes('architect') || stage.includes('design')) {
        if (stage.includes('thinking')) return 'thinking'
        if (stage.includes('starting')) return 'starting'
        if (stage.includes('executing')) return 'executing'
        if (stage.includes('completed') || stage.includes('complete')) return 'completed'
        return 'active'
      }
      if (getStageStatus('pm') === 'completed') return 'completed'
      return 'pending'
    } else if (stageId === 'eng') {
      if (role.includes('engineer') || stage.includes('code')) {
        if (stage.includes('thinking')) return 'thinking'
        if (stage.includes('starting')) return 'starting'
        if (stage.includes('executing')) return 'executing'
        if (stage.includes('completed') || stage.includes('complete')) return 'completed'
        return 'active'
      }
      if (getStageStatus('arch') === 'completed') return 'completed'
      return 'pending'
    }
    
    return 'pending'
  }

  return (
    <div className="flex-1 flex min-h-0 bg-background">
      {/* Left Sidebar - File Tree */}
      <div className="w-64 border-l border-border flex flex-col bg-card min-h-0">
        {/* Header with Progress Toggle */}
        <div className="flex-shrink-0 p-3 border-b border-border">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-sm">EXPLORER</h2>
            <button
              onClick={() => setShowProgress(!showProgress)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              <Activity className="w-4 h-4" />
            </button>
          </div>
          {showProgress && currentTask && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{currentTask.progress}%</span>
              </div>
              <Progress value={currentTask.progress} className="h-1.5" />
              <div className="flex items-center gap-2 text-xs">
                {stages.map((stage) => {
                  const status = getStageStatus(stage.id)
                  const StageIcon = stage.icon
                  return (
                    <div key={stage.id} className="flex items-center gap-1">
                      {status === 'completed' && <CheckCircle2 className="w-3 h-3 text-green-500" />}
                      {status === 'thinking' && <Brain className="w-3 h-3 text-blue-500 animate-pulse" />}
                      {(status === 'starting' || status === 'executing') && <Loader2 className="w-3 h-3 text-primary animate-spin" />}
                      {status === 'pending' && <Circle className="w-3 h-3 text-muted-foreground" />}
                      <StageIcon className="w-3 h-3 text-muted-foreground" />
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* File Tree */}
        <ScrollArea className="flex-1">
          <div className="p-2">
            {fileTree.length === 0 ? (
              <div className="text-xs text-muted-foreground p-4 text-center">
                Generated files will appear here
              </div>
            ) : (
              <div className="space-y-0.5">
                {fileTree.map(node => renderTreeNode(node))}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Right Side - File Editor */}
      <div className="flex-1 flex flex-col min-h-0 bg-background">
        {selectedFileContent ? (
          <>
            {/* File Header */}
            <div className="flex-shrink-0 p-2 border-b border-border bg-secondary flex items-center justify-between">
              <div className="flex items-center gap-2">
                <File className="w-4 h-4 text-muted-foreground" />
                <p className="text-sm font-medium truncate">{selectedFileContent.path}</p>
              </div>
              {streamingFiles.has(selectedFileContent.path) && (
                <div className="flex items-center gap-2 text-xs text-primary">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Writing...</span>
                </div>
              )}
            </div>

            {/* File Content */}
            <div className="flex-1 min-h-0 overflow-hidden bg-[#1e1e1e]">
              <ScrollArea className="h-full">
                {selectedFileContent.type === 'source' ? (
                  <div className="relative">
                    <SyntaxHighlighter
                      language={getLanguage(selectedFileContent.path)}
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        padding: '1rem',
                        fontSize: '0.875rem',
                        lineHeight: '1.5',
                        background: 'transparent'
                      }}
                      showLineNumbers
                      wrapLines
                    >
                      {selectedFileContent.content}
                    </SyntaxHighlighter>
                    {streamingFiles.has(selectedFileContent.path) && (
                      <span className="absolute bottom-4 right-4 text-primary animate-pulse">▊</span>
                    )}
                  </div>
                ) : (
                  <div className="p-4 bg-background">
                    <pre className="text-sm font-mono whitespace-pre-wrap text-foreground">
                      <code>{selectedFileContent.content}</code>
                      {streamingFiles.has(selectedFileContent.path) && (
                        <span className="animate-pulse text-primary">▊</span>
                      )}
                    </pre>
                  </div>
                )}
              </ScrollArea>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
            <div className="text-center">
              <File className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Select a file to view its content</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

