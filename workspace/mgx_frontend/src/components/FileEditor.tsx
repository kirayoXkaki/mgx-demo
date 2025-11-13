import { useState, useEffect, useMemo } from 'react'
import { File, Folder, FolderOpen, ChevronRight, ChevronDown, Loader2, CheckCircle2, Circle, Brain, FileText, Code, Activity } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { ScrollArea } from './ui/scroll-area'
import { Progress } from './ui/progress'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'

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

  // Reset UI when files are cleared (new chat)
  useEffect(() => {
    if (files.length === 0 && streamingFiles.size === 0) {
      setSelectedFile(null)
      setExpandedFolders(new Set())
    }
  }, [files.length, streamingFiles.size])

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
      const content = streamingFiles.get(filepath) || ''
      // Debug: log when getting streaming content
      if (content.length > 0 && content.length % 100 === 0) {
        console.log('📖 [FileEditor] Getting streaming content for', filepath, 'length:', content.length)
      }
      return content
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
            className={`w-full flex items-center gap-1 py-1 px-2 text-sm rounded-lg hover:bg-gradient-to-r hover:from-pink-100 hover:to-purple-100 dark:hover:from-pink-900 dark:hover:to-purple-900 transition-all ${
              isSelected ? 'bg-gradient-to-r from-pink-200 to-purple-200 dark:from-pink-800 dark:to-purple-800' : ''
            }`}
            style={{ paddingLeft: `${8 + level * 16}px` }}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-pink-600 dark:text-pink-400" />
            ) : (
              <ChevronRight className="w-3 h-3 text-pink-600 dark:text-pink-400" />
            )}
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 text-pink-500" />
            ) : (
              <Folder className="w-4 h-4 text-pink-500" />
            )}
            <span className="flex-1 text-left truncate text-pink-900 dark:text-pink-100">{node.name}</span>
            {(node.isStreaming || hasStreamingChild) && (
              <Loader2 className="w-3 h-3 text-pink-600 dark:text-pink-400 animate-spin" />
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
          className={`w-full flex items-center gap-2 py-1 px-2 text-sm rounded-lg hover:bg-gradient-to-r hover:from-pink-100 hover:to-purple-100 dark:hover:from-pink-900 dark:hover:to-purple-900 transition-all ${
            isSelected ? 'bg-gradient-to-r from-pink-200 to-purple-200 dark:from-pink-800 dark:to-purple-800 border-l-4 border-pink-500' : ''
          } ${isStreaming ? 'border-l-4 border-pink-500' : ''}`}
          style={{ paddingLeft: `${8 + level * 16}px` }}
        >
          <File className="w-4 h-4 text-pink-600 dark:text-pink-400" />
          <span className="flex-1 text-left truncate text-pink-900 dark:text-pink-100">{node.name}</span>
          {isStreaming && (
            <>
              <Loader2 className="w-3 h-3 text-pink-600 dark:text-pink-400 animate-spin" />
              <span className="text-xs text-pink-600 dark:text-pink-400">Writing...</span>
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
    <div className="flex-1 flex min-h-0 bg-background h-full">
      <PanelGroup direction="horizontal" className="h-full">
        {/* Left Sidebar - File Tree */}
        <Panel defaultSize={20} minSize={15} maxSize={35} className="min-w-0">
          <div className="w-full h-full border-l border-pink-200 dark:border-pink-800 flex flex-col bg-gradient-to-b from-white/80 via-pink-50/80 to-purple-50/80 dark:from-purple-950/80 dark:via-pink-950/80 dark:to-purple-950/80 backdrop-blur-sm min-h-0">
            {/* Header with Progress Toggle */}
            <div className="flex-shrink-0 p-3 border-b border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-900 dark:to-purple-900">
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold text-sm bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">EXPLORER</h2>
                <button
                  onClick={() => setShowProgress(!showProgress)}
                  className="text-xs text-pink-600 dark:text-pink-400 hover:text-pink-700 dark:hover:text-pink-300 transition-colors"
                >
                  <Activity className="w-4 h-4" />
                </button>
              </div>
              {showProgress && currentTask && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-pink-700 dark:text-pink-300">Progress</span>
                    <span className="font-medium text-pink-900 dark:text-pink-100">{currentTask.progress}%</span>
                  </div>
                  <Progress value={currentTask.progress} className="h-1.5" />
                  <div className="flex items-center gap-2 text-xs">
                    {stages.map((stage) => {
                      const status = getStageStatus(stage.id)
                      const StageIcon = stage.icon
                      return (
                        <div key={stage.id} className="flex items-center gap-1">
                          {status === 'completed' && <CheckCircle2 className="w-3 h-3 text-pink-500" />}
                          {status === 'thinking' && <Brain className="w-3 h-3 text-purple-500 animate-pulse" />}
                          {(status === 'starting' || status === 'executing') && <Loader2 className="w-3 h-3 text-pink-600 dark:text-pink-400 animate-spin" />}
                          {status === 'pending' && <Circle className="w-3 h-3 text-pink-400 dark:text-pink-600" />}
                          <StageIcon className="w-3 h-3 text-pink-600 dark:text-pink-400" />
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
                  <div className="text-xs text-pink-600 dark:text-pink-400 p-4 text-center">
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
        </Panel>
        
        {/* Resize Handle for File Tree */}
        <PanelResizeHandle className="w-1 bg-pink-200 dark:bg-pink-800 hover:bg-pink-300 dark:hover:bg-pink-700 transition-colors relative group">
          <div className="absolute inset-y-0 left-1/2 transform -translate-x-1/2 w-0.5 bg-pink-400 dark:bg-pink-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </PanelResizeHandle>

        {/* Right Side - File Editor */}
        <Panel defaultSize={80} minSize={65} className="min-w-0">
          <div className="w-full h-full flex flex-col min-h-0 bg-background">
            {selectedFileContent ? (
              <>
                {/* File Header */}
                <div className="flex-shrink-0 p-2 border-b border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-900 dark:to-purple-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <File className="w-4 h-4 text-pink-600 dark:text-pink-400" />
                    <p className="text-sm font-medium truncate text-pink-900 dark:text-pink-100">{selectedFileContent.path}</p>
                  </div>
                  {streamingFiles.has(selectedFileContent.path) && (
                    <div className="flex items-center gap-2 text-xs text-pink-600 dark:text-pink-400">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>Writing...</span>
                    </div>
                  )}
                </div>

                {/* File Content */}
                <div className="flex-1 min-h-0 overflow-hidden bg-[#1e1e1e]">
                  <ScrollArea className="h-full">
                    {selectedFileContent.type === 'source' && getLanguage(selectedFileContent.path) !== 'markdown' ? (
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
                      <div className="p-4 bg-background min-h-full">
                        {getLanguage(selectedFileContent.path) === 'markdown' ? (
                      <div className="text-sm leading-relaxed text-foreground">
                        {selectedFileContent.content.split('\n').map((line, index) => {
                          // Simple markdown rendering without syntax highlighting overlay
                          if (line.startsWith('# ')) {
                            return <h1 key={index} className="text-2xl font-bold text-pink-600 dark:text-pink-400 mt-4 mb-2">{line.substring(2)}</h1>
                          }
                          if (line.startsWith('## ')) {
                            return <h2 key={index} className="text-xl font-bold text-pink-600 dark:text-pink-400 mt-3 mb-2">{line.substring(3)}</h2>
                          }
                          if (line.startsWith('### ')) {
                            return <h3 key={index} className="text-lg font-bold text-purple-600 dark:text-purple-400 mt-2 mb-1">{line.substring(4)}</h3>
                          }
                          if (line.startsWith('#### ')) {
                            return <h4 key={index} className="text-base font-bold text-purple-500 dark:text-purple-400 mt-2 mb-1">{line.substring(5)}</h4>
                          }
                          if (line.startsWith('- ') || line.startsWith('* ')) {
                            return <div key={index} className="ml-4 text-foreground mb-1">• {line.substring(2)}</div>
                          }
                          if (line.match(/^\d+\.\s/)) {
                            return <div key={index} className="ml-4 text-foreground mb-1">{line}</div>
                          }
                          if (line.trim() === '') {
                            return <br key={index} />
                          }
                          if (line.startsWith('```')) {
                            return <div key={index} className="my-2 px-2 py-1 bg-pink-100 dark:bg-pink-900 rounded text-pink-600 dark:text-pink-400 font-semibold font-mono text-xs">{line}</div>
                          }
                          // Check for inline code
                          if (line.includes('`')) {
                            const parts = line.split('`')
                            return (
                              <div key={index} className="text-foreground mb-1">
                                {parts.map((part, i) => 
                                  i % 2 === 0 ? (
                                    <span key={i}>{part}</span>
                                  ) : (
                                    <code key={i} className="bg-pink-100 dark:bg-pink-900 px-1 rounded text-pink-600 dark:text-pink-400 font-mono text-xs">{part}</code>
                                  )
                                )}
                              </div>
                            )
                          }
                          return <div key={index} className="text-foreground mb-1">{line}</div>
                        })}
                        {streamingFiles.has(selectedFileContent.path) && (
                          <span className="inline-block w-2 h-4 bg-pink-500 dark:bg-pink-400 ml-1 animate-pulse">▊</span>
                        )}
                      </div>
                    ) : (
                      <pre className="text-sm font-mono whitespace-pre-wrap text-foreground">
                        <code>{selectedFileContent.content}</code>
                        {streamingFiles.has(selectedFileContent.path) && (
                          <span className="inline-block w-2 h-4 bg-pink-500 dark:bg-pink-400 ml-1 animate-pulse">▊</span>
                        )}
                      </pre>
                    )}
                  </div>
                    )}
                  </ScrollArea>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-sm text-pink-600 dark:text-pink-400 relative overflow-hidden">
                {/* Decorative background elements */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute top-20 left-20 w-32 h-32 bg-pink-300 dark:bg-pink-700 rounded-full blur-3xl animate-float" style={{ animationDelay: '0s' }}></div>
                  <div className="absolute bottom-20 right-20 w-40 h-40 bg-purple-300 dark:bg-purple-700 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-yellow-300 dark:bg-yellow-700 rounded-full blur-2xl animate-float" style={{ animationDelay: '0.5s' }}></div>
                </div>
                
                <div className="text-center relative z-10 space-y-6 animate-fade-in">
                  <div className="relative">
                    <div className="absolute -top-4 -left-4 w-16 h-16 bg-pink-200 dark:bg-pink-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '0s' }}></div>
                    <div className="absolute -top-2 -right-6 w-12 h-12 bg-purple-200 dark:bg-purple-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '0.5s' }}></div>
                    <div className="absolute -bottom-4 left-8 w-10 h-10 bg-yellow-200 dark:bg-yellow-800 rounded-full opacity-30 animate-float" style={{ animationDelay: '1s' }}></div>
                    
                    <div className="relative bg-gradient-to-br from-pink-100 via-purple-100 to-pink-100 dark:from-pink-900 dark:via-purple-900 dark:to-pink-900 rounded-2xl p-8 border-2 border-pink-300 dark:border-pink-600 pokemon-shadow max-w-md mx-auto">
                      <div className="text-6xl mb-4 animate-bounce">📁</div>
                      <h3 className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent mb-2">
                        File Explorer
                      </h3>
                      <p className="text-sm text-pink-700 dark:text-pink-300 mb-4">
                        Your generated files will appear here
                      </p>
                      
                      <div className="space-y-2 text-left mt-6">
                        <div className="flex items-center gap-2 text-xs text-pink-600 dark:text-pink-400">
                          <FileText className="w-4 h-4" />
                          <span>Documents and specifications</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-purple-600 dark:text-purple-400">
                          <Code className="w-4 h-4" />
                          <span>Source code files</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-yellow-600 dark:text-yellow-400">
                          <File className="w-4 h-4" />
                          <span>Project structure</span>
                        </div>
                      </div>
                      
                      <div className="absolute top-2 right-2 text-2xl opacity-20 animate-pulse">✨</div>
                      <div className="absolute bottom-2 left-2 text-xl opacity-20 animate-pulse" style={{ animationDelay: '0.5s' }}>⭐</div>
                    </div>
                  </div>
                  
                  <p className="text-xs text-pink-500 dark:text-pink-500">
                    Files will appear as your team generates them
                  </p>
                </div>
              </div>
            )}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  )
}

