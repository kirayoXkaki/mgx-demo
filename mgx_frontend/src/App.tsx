import { useState } from 'react'
import { Header } from './components/Header'
import { ChatPanel } from './components/ChatPanel'
import { ProgressPanel } from './components/ProgressPanel'
import { FileExplorer } from './components/FileExplorer'
import { TaskProvider } from './hooks/useTask'

function App() {
  return (
    <TaskProvider>
      <div className="h-screen flex flex-col bg-background overflow-hidden">
        <Header />
        <div className="flex-1 flex min-h-0">
          <ChatPanel />
          <ProgressPanel />
          <FileExplorer />
        </div>
      </div>
    </TaskProvider>
  )
}

export default App