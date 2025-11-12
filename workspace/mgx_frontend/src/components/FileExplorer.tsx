import { useState, useEffect } from 'react'
import { File, Folder, FolderOpen, Loader2 } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { ScrollArea } from './ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

export function FileExplorer() {
  const { files, streamingFiles } = useTask()
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  // Auto-select first streaming file or listen for file selection events
  useEffect(() => {
    if (streamingFiles.size > 0) {
      const streamingFileList = Array.from(streamingFiles.keys())
      // Auto-select the most recently added streaming file
      if (!selectedFile || !streamingFiles.has(selectedFile)) {
        const latestFile = streamingFileList[streamingFileList.length - 1]
        setSelectedFile(latestFile)
      }
    }
    
    // Listen for file selection events
    const handleFileSelected = (event: CustomEvent) => {
      if (event.detail?.filepath) {
        setSelectedFile(event.detail.filepath)
      }
    }
    
    window.addEventListener('fileSelected', handleFileSelected as EventListener)
    return () => {
      window.removeEventListener('fileSelected', handleFileSelected as EventListener)
    }
  }, [streamingFiles, selectedFile])
  
  // Get file content (prioritize streaming content)
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
    type: selectedFile.includes('src/') ? 'source' : 'document' as const
  } : null
  
  // Combine files and streaming files
  const allFiles = [
    ...files,
    ...Array.from(streamingFiles.entries())
      .filter(([path]) => !files.find(f => f.path === path))
      .map(([path, content]) => ({
        path,
        content,
        type: (path.includes('src/') ? 'source' : 'document') as const
      }))
  ]

  const groupedFiles = allFiles.reduce((acc, file) => {
    const parts = file.path.split('/')
    const folder = parts[0] || 'root'
    if (!acc[folder]) acc[folder] = []
    acc[folder].push(file)
    return acc
  }, {} as Record<string, typeof allFiles>)

  return (
    <div className="w-96 border-l border-border flex flex-col bg-card min-h-0">
      <div className="flex-shrink-0 p-4 border-b border-border">
        <h2 className="font-semibold text-lg">Files</h2>
      </div>
      
      {allFiles.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground p-6 text-center">
          Generated files will appear here
        </div>
      ) : (
        <Tabs defaultValue="explorer" className="flex-1 flex flex-col min-h-0">
          <TabsList className="flex-shrink-0 mx-4 mt-4">
            <TabsTrigger value="explorer">Explorer</TabsTrigger>
            <TabsTrigger value="viewer">Viewer</TabsTrigger>
          </TabsList>
          
          <TabsContent value="explorer" className="flex-1 flex flex-col overflow-hidden mt-0 min-h-0">
            <div className="flex-1 min-h-0 overflow-hidden">
            <ScrollArea className="h-full p-4">
              <div className="space-y-2">
                {Object.entries(groupedFiles).map(([folder, folderFiles]) => (
                  <div key={folder}>
                    <div className="flex items-center gap-2 py-1 px-2 text-sm font-medium">
                      <FolderOpen className="w-4 h-4 text-yellow-500" />
                      {folder}
                    </div>
                    <div className="ml-4 space-y-1">
                      {folderFiles.map((file) => {
                        const isStreaming = streamingFiles.has(file.path)
                        return (
                        <button
                          key={file.path}
                          onClick={() => setSelectedFile(file.path)}
                          className={`w-full flex items-center gap-2 py-1 px-2 text-sm rounded hover:bg-accent ${
                            selectedFile === file.path ? 'bg-accent' : ''
                            } ${isStreaming ? 'border-l-2 border-primary' : ''}`}
                        >
                            {isStreaming && <Loader2 className="w-3 h-3 text-primary animate-spin" />}
                          <File className="w-4 h-4" />
                            <span className="flex-1 text-left">{file.path.split('/').pop()}</span>
                            {isStreaming && (
                              <span className="text-xs text-primary">Writing...</span>
                            )}
                        </button>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            </div>
          </TabsContent>
          
          <TabsContent value="viewer" className="flex-1 flex flex-col overflow-hidden mt-0 min-h-0">
            {selectedFileContent ? (
              <div className="flex-1 flex flex-col min-h-0">
                <div className="flex-shrink-0 p-3 border-b border-border bg-secondary flex items-center justify-between">
                  <p className="text-sm font-medium truncate">{selectedFileContent.path}</p>
                  {streamingFiles.has(selectedFileContent.path) && (
                    <div className="flex items-center gap-2 text-xs text-primary">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>Writing...</span>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-h-0 overflow-hidden">
                  <ScrollArea className="h-full">
                  <pre className="p-4 text-xs font-mono">
                      <code className="whitespace-pre-wrap">{selectedFileContent.content}</code>
                      {streamingFiles.has(selectedFileContent.path) && (
                        <span className="animate-pulse">▊</span>
                      )}
                  </pre>
                </ScrollArea>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
                Select a file to view its content
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}