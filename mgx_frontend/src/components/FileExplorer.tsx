import { useState } from 'react'
import { File, Folder, FolderOpen } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { ScrollArea } from './ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

export function FileExplorer() {
  const { files } = useTask()
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const selectedFileContent = files.find(f => f.path === selectedFile)

  const groupedFiles = files.reduce((acc, file) => {
    const parts = file.path.split('/')
    const folder = parts[0]
    if (!acc[folder]) acc[folder] = []
    acc[folder].push(file)
    return acc
  }, {} as Record<string, typeof files>)

  return (
    <div className="w-96 border-l border-border flex flex-col bg-card">
      <div className="p-4 border-b border-border">
        <h2 className="font-semibold text-lg">Files</h2>
      </div>
      
      {files.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground p-6 text-center">
          Generated files will appear here
        </div>
      ) : (
        <Tabs defaultValue="explorer" className="flex-1 flex flex-col">
          <TabsList className="mx-4 mt-4">
            <TabsTrigger value="explorer">Explorer</TabsTrigger>
            <TabsTrigger value="viewer">Viewer</TabsTrigger>
          </TabsList>
          
          <TabsContent value="explorer" className="flex-1 overflow-hidden mt-0">
            <ScrollArea className="h-full p-4">
              <div className="space-y-2">
                {Object.entries(groupedFiles).map(([folder, folderFiles]) => (
                  <div key={folder}>
                    <div className="flex items-center gap-2 py-1 px-2 text-sm font-medium">
                      <FolderOpen className="w-4 h-4 text-yellow-500" />
                      {folder}
                    </div>
                    <div className="ml-4 space-y-1">
                      {folderFiles.map((file) => (
                        <button
                          key={file.path}
                          onClick={() => setSelectedFile(file.path)}
                          className={`w-full flex items-center gap-2 py-1 px-2 text-sm rounded hover:bg-accent ${
                            selectedFile === file.path ? 'bg-accent' : ''
                          }`}
                        >
                          <File className="w-4 h-4" />
                          {file.path.split('/').pop()}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="viewer" className="flex-1 overflow-hidden mt-0">
            {selectedFileContent ? (
              <div className="h-full flex flex-col">
                <div className="p-3 border-b border-border bg-secondary">
                  <p className="text-sm font-medium truncate">{selectedFileContent.path}</p>
                </div>
                <ScrollArea className="flex-1">
                  <pre className="p-4 text-xs font-mono">
                    <code>{selectedFileContent.content}</code>
                  </pre>
                </ScrollArea>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
                Select a file to view its content
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}