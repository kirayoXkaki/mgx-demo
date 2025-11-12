import { useState } from 'react'
import { Rocket, DollarSign, Download, Github, Loader2, User, Mail, ExternalLink, Linkedin, Settings, LogOut, UserCircle, History } from 'lucide-react'
import { useTask } from '../hooks/useTask'
import { useAuth } from '../hooks/useAuth'
import { formatCost } from '../lib/utils'
import { Button } from './ui/button'
import { ConversationHistory } from './ConversationHistory'

export function Header() {
  const { currentTask, downloadProject } = useTask()
  const { user, logout, isAuthenticated } = useAuth()
  const [showGitHubDialog, setShowGitHubDialog] = useState(false)
  const [showAboutDialog, setShowAboutDialog] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [githubToken, setGithubToken] = useState('')
  const [repoName, setRepoName] = useState('')
  const [repoDescription, setRepoDescription] = useState('')
  const [isPrivate, setIsPrivate] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')

  const handleGitHubUpload = async () => {
    if (!currentTask?.task_id) return
    
    if (!githubToken.trim()) {
      setUploadError('Please enter your GitHub token')
      return
    }
    
    if (!repoName.trim()) {
      setUploadError('Please enter a repository name')
      return
    }
    
    setIsUploading(true)
    setUploadError('')
    setUploadSuccess('')
    
    try {
      const response = await fetch('/api/github/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: currentTask.task_id,
          repo_name: repoName.trim(),
          description: repoDescription.trim(),
          is_private: isPrivate,
          github_token: githubToken.trim(),
        }),
      })
      
      if (!response.ok) {
        let errorMessage = 'Failed to upload to GitHub'
        try {
          const data = await response.json()
          errorMessage = data.detail || data.message || errorMessage
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }
      
      const data = await response.json()
      
      setUploadSuccess(data.message || 'Successfully uploaded to GitHub!')
      // Open the repository in a new tab
      if (data.repo_url) {
        setTimeout(() => {
          window.open(data.repo_url, '_blank')
        }, 1000)
      }
      
      // Close dialog after 2 seconds
      setTimeout(() => {
        setShowGitHubDialog(false)
        setGithubToken('')
        setRepoName('')
        setRepoDescription('')
        setIsPrivate(false)
        setUploadSuccess('')
      }, 2000)
    } catch (error) {
      console.error('GitHub upload error:', error)
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        setUploadError('Network error: Could not connect to server. Please check if the backend is running.')
      } else {
        setUploadError(error instanceof Error ? error.message : 'Failed to upload to GitHub')
      }
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <header className="h-14 border-b border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-100 via-purple-100 to-pink-100 dark:from-pink-900 dark:via-purple-900 dark:to-pink-900 flex items-center justify-between px-6 pokemon-shadow">
      <div className="flex items-center gap-3">
        <div className="animate-float">
          <Rocket className="w-6 h-6 text-pink-600 dark:text-pink-400" />
        </div>
        <h1 className="text-xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-pink-600 dark:from-pink-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent">MGX Demo</h1>
        <span className="text-sm text-pink-700 dark:text-pink-300">AI Software Development Platform</span>
      </div>
      
      <div className="flex items-center gap-4">
        {currentTask && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-gradient-to-r from-pink-200 to-purple-200 dark:from-pink-800 dark:to-purple-800 border border-pink-300 dark:border-pink-600 pokemon-shadow">
            <DollarSign className="w-4 h-4 text-pink-700 dark:text-pink-300" />
            <span className="text-sm font-medium text-pink-900 dark:text-pink-100">
              Cost: {formatCost(currentTask.cost)}
            </span>
          </div>
        )}
        
        {currentTask?.status === 'completed' && (
          <>
            <Button 
              onClick={() => setShowGitHubDialog(true)} 
              size="sm" 
              className="gap-2 bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white font-semibold rounded-xl transition-all transform hover:scale-105"
            >
              <Github className="w-4 h-4" />
              Upload to GitHub
            </Button>
            <Button onClick={downloadProject} size="sm" className="gap-2 pokemon-gradient hover:pokemon-glow text-white font-semibold rounded-xl transition-all transform hover:scale-105">
              <Download className="w-4 h-4" />
              Download Project
            </Button>
          </>
        )}
        
        {/* History Button */}
        {isAuthenticated && user && (
          <Button
            onClick={() => setShowHistory(true)}
            size="sm"
            variant="ghost"
            className="gap-2 text-pink-700 dark:text-pink-300 hover:bg-pink-100 dark:hover:bg-pink-900 rounded-xl transition-all transform hover:scale-105"
          >
            <History className="w-4 h-4" />
            历史记录
          </Button>
        )}
        
        {/* User Menu */}
        {isAuthenticated && user ? (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-pink-200 to-purple-200 dark:from-pink-800 dark:to-purple-800 border border-pink-300 dark:border-pink-600 hover:from-pink-300 hover:to-purple-300 dark:hover:from-pink-700 dark:hover:to-purple-700 transition-all pokemon-shadow"
            >
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.username} className="w-6 h-6 rounded-full" />
              ) : (
                <UserCircle className="w-5 h-5 text-pink-700 dark:text-pink-300" />
              )}
              <span className="text-sm font-medium text-pink-900 dark:text-pink-100">{user.username}</span>
            </button>
            
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-pink-200 dark:border-pink-800 pokemon-shadow z-50">
                <div className="p-2">
                  <button
                    onClick={() => {
                      setShowSettings(true)
                      setShowUserMenu(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-pink-50 dark:hover:bg-pink-900/30 text-pink-700 dark:text-pink-300 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    Settings
                  </button>
                  <button
                    onClick={() => {
                      logout()
                      setShowUserMenu(false)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : null}
        
        {/* About Developer Button */}
        <Button 
          onClick={() => setShowAboutDialog(true)} 
          size="sm" 
          variant="ghost"
          className="gap-2 text-pink-700 dark:text-pink-300 hover:bg-pink-100 dark:hover:bg-pink-900 rounded-xl transition-all transform hover:scale-105"
        >
          <User className="w-4 h-4" />
          About Developer
        </Button>
      </div>
      
      {/* GitHub Upload Dialog */}
      {showGitHubDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md pokemon-shadow border-2 border-pink-300 dark:border-pink-600">
            <h2 className="text-xl font-bold mb-4 bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
              Upload to GitHub
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-1">
                  GitHub Personal Access Token *
                </label>
                <input
                  type="password"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxx or github_pat_xxxxxxxxxxxx"
                  className="w-full px-3 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
                />
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-pink-600 dark:text-pink-400">
                    <strong>Tip:</strong> Classic token is easier to set up
                  </p>
                  <div className="text-xs text-pink-600 dark:text-pink-400 space-y-1">
                    <div>
                      <p>• <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="underline font-semibold">Classic token</a> (recommended - easier)</p>
                      <p className="ml-4 text-pink-500 dark:text-pink-500">Required scope: <code className="bg-pink-100 dark:bg-pink-900 px-1 rounded">repo</code> (full control of private repositories)</p>
                    </div>
                    <div>
                      <p>• <a href="https://github.com/settings/tokens?type=beta" target="_blank" rel="noopener noreferrer" className="underline">Fine-grained token</a> (advanced)</p>
                      <p className="ml-4 text-pink-500 dark:text-pink-500">
                        Required permissions:<br/>
                        - <strong>Administration: Write</strong> (for creating repos)<br/>
                        - Contents: Read/Write<br/>
                        - Metadata: Read
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-1">
                  Repository Name *
                </label>
                <input
                  type="text"
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                  placeholder="my-awesome-project"
                  className="w-full px-3 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-1">
                  Description
                </label>
                <textarea
                  value={repoDescription}
                  onChange={(e) => setRepoDescription(e.target.value)}
                  placeholder="A project generated by MGX"
                  rows={2}
                  className="w-full px-3 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isPrivate"
                  checked={isPrivate}
                  onChange={(e) => setIsPrivate(e.target.checked)}
                  className="w-4 h-4 text-pink-600 border-pink-300 rounded focus:ring-pink-500"
                />
                <label htmlFor="isPrivate" className="text-sm text-pink-700 dark:text-pink-300">
                  Make repository private
                </label>
              </div>
              
              {uploadError && (
                <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-600 rounded-lg text-red-700 dark:text-red-300 text-sm">
                  {uploadError}
                </div>
              )}
              
              {uploadSuccess && (
                <div className="p-3 bg-green-100 dark:bg-green-900 border border-green-300 dark:border-green-600 rounded-lg text-green-700 dark:text-green-300 text-sm">
                  {uploadSuccess}
                </div>
              )}
              
              <div className="flex gap-3 pt-2">
                <Button
                  onClick={handleGitHubUpload}
                  disabled={isUploading || !githubToken.trim() || !repoName.trim()}
                  className="flex-1 gap-2 pokemon-gradient hover:pokemon-glow text-white font-semibold rounded-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Github className="w-4 h-4" />
                      Upload
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => {
                    setShowGitHubDialog(false)
                    setGithubToken('')
                    setRepoName('')
                    setRepoDescription('')
                    setIsPrivate(false)
                    setUploadError('')
                    setUploadSuccess('')
                  }}
                  className="px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-xl"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* About Developer Dialog */}
      {showAboutDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowAboutDialog(false)}>
          <div 
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-lg pokemon-shadow border-2 border-pink-300 dark:border-pink-600 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
                About Developer
              </h2>
              <button
                onClick={() => setShowAboutDialog(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Developer Avatar and Name */}
              <div className="flex items-center gap-4 pb-4 border-b border-pink-200 dark:border-pink-800">
                <div className="flex-shrink-0 w-20 h-20 rounded-full bg-gradient-to-br from-pink-200 to-pink-300 dark:from-pink-700 dark:to-pink-800 border-2 border-pink-400 dark:border-pink-500 flex items-center justify-center shadow-md overflow-hidden">
                  <img 
                    src="/pokemon/sylveon.png" 
                    alt="Naordo"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.style.display = 'none'
                      const parent = target.parentElement
                      if (parent) {
                        parent.innerHTML = '🌸'
                        parent.className += ' text-4xl'
                      }
                    }}
                  />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-pink-900 dark:text-pink-100">Naordo</h3>
                  <p className="text-sm text-pink-600 dark:text-pink-400">Game Mod Developer & Full-Stack Developer</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Mail className="w-4 h-4 text-pink-600 dark:text-pink-400" />
                    <a 
                      href="mailto:jianzhix@usc.edu" 
                      className="text-sm text-pink-600 dark:text-pink-400 hover:text-pink-700 dark:hover:text-pink-300 hover:underline"
                    >
                      jianzhix@usc.edu
                    </a>
                  </div>
                </div>
              </div>
              
              {/* Social Links */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-pink-700 dark:text-pink-300 uppercase tracking-wide">Connect</h4>
                
                <div className="space-y-2">
                  <a
                    href="https://github.com/kirayoXkaki/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 hover:from-gray-100 hover:to-gray-200 dark:hover:from-gray-600 dark:hover:to-gray-700 border border-gray-200 dark:border-gray-600 transition-all transform hover:scale-105 pokemon-shadow"
                  >
                    <Github className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">GitHub</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">@kirayoXkaki</div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  </a>
                  
                  <a
                    href="https://space.bilibili.com/1211284883"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900 dark:to-cyan-900 hover:from-blue-100 hover:to-cyan-100 dark:hover:from-blue-800 dark:hover:to-cyan-800 border border-blue-200 dark:border-blue-700 transition-all transform hover:scale-105 pokemon-shadow"
                  >
                    <div className="w-5 h-5 flex items-center justify-center">
                      <img 
                        src="https://www.bilibili.com/favicon.ico" 
                        alt="Bilibili"
                        className="w-5 h-5"
                        onError={(e) => {
                          // Fallback to Bilibili logo SVG
                          const target = e.target as HTMLImageElement
                          target.outerHTML = `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="#00A1D6" xmlns="http://www.w3.org/2000/svg"><path d="M8.5 3.5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7c1.1 0 2-.9 2-2v-12c0-1.1-.9-2-2-2h-7zm0 1h7c.6 0 1 .4 1 1v12c0 .6-.4 1-1 1h-7c-.6 0-1-.4-1-1v-12c0-.6.4-1 1-1zm1.5 2.5v9h6v-9h-6z"/></svg>`
                        }}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Bilibili</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">游戏mod开发者</div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  </a>
                  
                  <a
                    href="https://www.linkedin.com/in/jianzhi-xu-407a16328/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 hover:from-blue-100 hover:to-indigo-100 dark:hover:from-blue-800 dark:hover:to-indigo-800 border border-blue-200 dark:border-blue-700 transition-all transform hover:scale-105 pokemon-shadow"
                  >
                    <Linkedin className="w-5 h-5 text-[#0077B5]" />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">LinkedIn</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Jianzhi Xu</div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  </a>
                  
                  <a
                    href="https://afdian.com/a/11451411cao"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900 dark:to-purple-900 hover:from-pink-100 hover:to-purple-100 dark:hover:from-pink-800 dark:hover:to-purple-800 border border-pink-200 dark:border-pink-700 transition-all transform hover:scale-105 pokemon-shadow"
                  >
                    <div className="w-5 h-5 flex items-center justify-center">
                      <img 
                        src="https://afdian.com/favicon.ico" 
                        alt="爱发电"
                        className="w-5 h-5"
                        onError={(e) => {
                          // Fallback to Afdian logo SVG
                          const target = e.target as HTMLImageElement
                          target.outerHTML = `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="#946CE6" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>`
                        }}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">爱发电 (Afdian)</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">支持我的创作</div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  </a>
                </div>
              </div>
              
              {/* Description */}
              <div className="pt-4 border-t border-pink-200 dark:border-pink-800">
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  Game mod developer and full-stack project developer. Passionate about creating innovative solutions and sharing knowledge with the community.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* User Settings Dialog */}
      {showSettings && (
        <UserSettingsDialog onClose={() => setShowSettings(false)} />
      )}
      
      {/* Conversation History Dialog */}
      {showHistory && (
        <ConversationHistory onClose={() => setShowHistory(false)} />
      )}
    </header>
  )
}

function UserSettingsDialog({ onClose }: { onClose: () => void }) {
  const { user, updateUser } = useAuth()
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '')
  const [email, setEmail] = useState(user?.email || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSave = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    
    try {
      await updateUser({
        avatar_url: avatarUrl || undefined,
        email: email || undefined
      })
      setSuccess('Profile updated successfully!')
      setTimeout(() => {
        onClose()
      }, 1000)
    } catch (err: any) {
      setError(err.message || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div 
        className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md pokemon-shadow border-2 border-pink-300 dark:border-pink-600"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-xl font-bold mb-4 bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
          User Settings
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-1">
              Avatar URL
            </label>
            <input
              type="url"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://example.com/avatar.png"
              className="w-full px-3 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
            />
            {avatarUrl && (
              <div className="mt-2">
                <img src={avatarUrl} alt="Avatar preview" className="w-16 h-16 rounded-full border-2 border-pink-300 dark:border-pink-600" onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none'
                }} />
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-pink-700 dark:text-pink-300 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-pink-300 dark:border-pink-600 rounded-lg bg-white/80 dark:bg-purple-950/80 text-pink-900 dark:text-pink-100 focus:border-pink-400 dark:focus:border-pink-500 focus:ring-pink-300 dark:focus:ring-pink-700"
            />
          </div>
          
          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-600 rounded-lg text-red-700 dark:text-red-300 text-sm">
              {error}
            </div>
          )}
          
          {success && (
            <div className="p-3 bg-green-100 dark:bg-green-900 border border-green-300 dark:border-green-600 rounded-lg text-green-700 dark:text-green-300 text-sm">
              {success}
            </div>
          )}
          
          <div className="flex gap-3 pt-2">
            <Button
              onClick={handleSave}
              disabled={loading}
              className="flex-1 pokemon-gradient hover:pokemon-glow text-white font-semibold rounded-xl"
            >
              {loading ? 'Saving...' : 'Save'}
            </Button>
            <Button
              onClick={onClose}
              className="px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-xl"
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}