import { useState } from 'react'
import { Header } from './components/Header'
import { ChatPanel } from './components/ChatPanel'
import { ProgressPanel } from './components/ProgressPanel'
import { FileExplorer } from './components/FileExplorer'
import { TaskProvider } from './hooks/useTask'

function App() {
  return (
    <TaskProvider>
      <div className="h-screen flex flex-col bg-background">
        <Header />
        <div className="flex-1 flex overflow-hidden">
          <ChatPanel />
          <ProgressPanel />
          <FileExplorer />
        </div>
      </div>
    </TaskProvider>
  )
}

export default App