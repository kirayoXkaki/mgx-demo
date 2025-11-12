import { Header } from './components/Header'
import { ChatPanel } from './components/ChatPanel'
import { FileEditor } from './components/FileEditor'
import { TaskProvider } from './hooks/useTask'
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'

function App() {
  return (
    <TaskProvider>
      <div className="h-screen flex flex-col bg-background overflow-hidden">
        <Header />
        <PanelGroup direction="horizontal" className="flex-1 min-h-0">
          {/* Chat Panel - Default 35% width */}
          <Panel defaultSize={35} minSize={25} maxSize={60} className="min-w-0">
            <ChatPanel />
          </Panel>
          
          {/* Resize Handle */}
          <PanelResizeHandle className="w-2 bg-pink-200 dark:bg-pink-800 hover:bg-pink-300 dark:hover:bg-pink-700 transition-colors relative group">
            <div className="absolute inset-y-0 left-1/2 transform -translate-x-1/2 w-1 bg-pink-400 dark:bg-pink-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </PanelResizeHandle>
          
          {/* File Editor - Takes remaining space */}
          <Panel defaultSize={65} minSize={40} className="min-w-0">
            <FileEditor />
          </Panel>
        </PanelGroup>
      </div>
    </TaskProvider>
  )
}

export default App