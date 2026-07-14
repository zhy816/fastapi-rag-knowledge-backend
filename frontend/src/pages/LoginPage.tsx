import axios from 'axios'
import { useState, type FormEvent } from 'react'

import apiClient from '../api/client'
import type { TokenResponse, User } from '../types'

interface LoginPageProps {
  onLogin: (user: User) => void
}

function LoginPage({ onLogin }: LoginPageProps) {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await apiClient.post('/users/register', {
          username,
          password,
        })
      }

      const response = await apiClient.post<TokenResponse>('/users/login', {
        username,
        password,
      })

      localStorage.setItem('access_token', response.data.access_token)
      onLogin(response.data.user)
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '请求失败')
      } else {
        setError('发生未知错误')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-intro">
          <p className="eyebrow">RAG KNOWLEDGE ASSISTANT</p>
          <h1>让文档成为你的 AI 知识库</h1>
          <p>
            上传资料、构建向量知识库，并通过可追溯来源的 RAG 问答获取答案。
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>{isRegister ? '创建账号' : '欢迎登录'}</h2>

          <label>
            用户名
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="请输入用户名"
              required
            />
          </label>

          <label>
            密码
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="请输入密码"
              required
            />
          </label>

          {error && <p className="form-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? '请稍候...' : isRegister ? '注册并登录' : '登录'}
          </button>

          <button
            type="button"
            className="text-button"
            onClick={() => {
              setIsRegister(!isRegister)
              setError('')
            }}
          >
            {isRegister ? '已有账号？返回登录' : '没有账号？立即注册'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage