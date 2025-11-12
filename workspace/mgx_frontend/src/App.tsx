import { Header } from './components/Header'
import { ChatPanel } from './components/ChatPanel'
import { FileEditor } from './components/FileEditor'
import { LoginPage } from './components/LoginPage'
import { TaskProvider } from './hooks/useTask'
import { AuthProvider, useAuth } from './hooks/useAuth'
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'

function AppContent() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-purple-50 to-pink-50 dark:from-purple-950 dark:via-pink-950 dark:to-purple-950">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-pink-600 dark:text-pink-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage />
  }

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

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App