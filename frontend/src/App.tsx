import { useEffect, useState } from 'react'

import apiClient from './api/client'
import LoginPage from './pages/LoginPage'
import type { User } from './types'
import './App.css'
import DocumentsPage from './pages/DocumentsPage'

import ChatPage from './pages/ChatPage'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [checkingAuth, setCheckingAuth] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      setCheckingAuth(false)
      return
    }

    apiClient
      .get<User>('/users/me')
      .then((response) => {
        setUser(response.data)
      })
      .catch(() => {
        localStorage.removeItem('access_token')
      })
      .finally(() => {
        setCheckingAuth(false)
      })
  }, [])

  function handleLogout() {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  if (checkingAuth) {
    return <div className="loading-page">正在验证登录状态...</div>
  }

  if (!user) {
    return <LoginPage onLogin={setUser} />
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">RAG KNOWLEDGE ASSISTANT</p>
          <h1>智能知识库</h1>
        </div>

        <div className="user-actions">
          <span>你好，{user.username}</span>
          <button type="button" onClick={handleLogout}>
            退出登录
          </button>
        </div>
      </header>

        <main className="dashboard">
          <section className="welcome-panel">
            <h2>欢迎回来，{user.username}</h2>
            <p>上传文档、完成解析和向量化，然后开始知识库问答。</p>
          </section>

          <DocumentsPage />
           <ChatPage />
        </main>
    </div>
  )
}

export default App