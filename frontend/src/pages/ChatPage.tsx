import axios from 'axios'
import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import apiClient from '../api/client'
import type {
  ChatAskResult,
  ChatMessage,
  ChatSession,
  Document,
  SearchSource,
} from '../types'

function ChatPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [selectedSessionId, setSelectedSessionId] =
    useState<number | null>(null)

  const [documentId, setDocumentId] = useState('')
  const [title, setTitle] = useState('')
  const [question, setQuestion] = useState('')
  const [sources, setSources] = useState<SearchSource[]>([])

  const [creating, setCreating] = useState(false)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState('')

  const loadInitialData = useCallback(async () => {
    try {
      const [documentResponse, sessionResponse] = await Promise.all([
        apiClient.get<Document[]>('/documents/'),
        apiClient.get<ChatSession[]>('/chat/sessions'),
      ])

      setDocuments(documentResponse.data)
      setSessions(sessionResponse.data)

      if (sessionResponse.data.length > 0) {
        setSelectedSessionId((current) =>
          current ?? sessionResponse.data[0].id
        )
      }
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '聊天数据加载失败')
      }
    }
  }, [])

  const loadMessages = useCallback(async (sessionId: number) => {
    try {
      const response = await apiClient.get<ChatMessage[]>(
        `/chat/sessions/${sessionId}/messages`,
      )
      setMessages(response.data)
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '消息加载失败')
      }
    }
  }, [])

  useEffect(() => {
    void loadInitialData()
  }, [loadInitialData])

  useEffect(() => {
    if (selectedSessionId !== null) {
      setSources([])
      void loadMessages(selectedSessionId)
    } else {
      setMessages([])
    }
  }, [selectedSessionId, loadMessages])

  async function handleCreateSession(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!documentId) {
      setError('请选择一份文档')
      return
    }

    setCreating(true)
    setError('')

    try {
      const response = await apiClient.post<ChatSession>('/chat/sessions', {
        document_id: Number(documentId),
        title: title.trim() || '新会话',
      })

      setSessions((current) => [response.data, ...current])
      setSelectedSessionId(response.data.id)
      setTitle('')
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '创建会话失败')
      }
    } finally {
      setCreating(false)
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (selectedSessionId === null || !question.trim()) {
      return
    }

    setAsking(true)
    setError('')
    setSources([])

    try {
      const response = await apiClient.post<ChatAskResult>('/chat/ask', {
        session_id: selectedSessionId,
        question: question.trim(),
        top_k: 5,
      })

      setQuestion('')
      setSources(response.data.sources)
      await loadMessages(selectedSessionId)
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '问答请求失败')
      }
    } finally {
      setAsking(false)
    }
  }

  return (
    <section className="chat-panel">
      <aside className="chat-sidebar">
        <div className="section-heading compact">
          <div>
            <p className="eyebrow">CONVERSATIONS</p>
            <h2>知识库问答</h2>
          </div>
        </div>

        <form className="new-session-form" onSubmit={handleCreateSession}>
          <select
            value={documentId}
            onChange={(event) => setDocumentId(event.target.value)}
            required
          >
            <option value="">选择知识库文档</option>
            {documents.map((document) => (
              <option value={document.id} key={document.id}>
                {document.filename}（ID: {document.id}）
              </option>
            ))}
          </select>

          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="会话标题（可选）"
          />

          <button type="submit" disabled={creating}>
            {creating ? '创建中...' : '新建会话'}
          </button>
        </form>

        <div className="session-list">
          {sessions.map((session) => (
            <button
              type="button"
              key={session.id}
              className={
                session.id === selectedSessionId ? 'active' : ''
              }
              onClick={() => setSelectedSessionId(session.id)}
            >
              <strong>{session.title}</strong>
              <span>文档 ID：{session.document_id}</span>
            </button>
          ))}
        </div>
      </aside>

      <div className="chat-main">
        {error && <p className="status-message error">{error}</p>}

        {selectedSessionId === null ? (
          <div className="empty-chat">
            <h3>创建或选择一个聊天会话</h3>
            <p>每个会话会关联一份已经向量化的文档。</p>
          </div>
        ) : (
          <>
            <div className="messages">
              {messages.length === 0 ? (
                <div className="empty-chat">
                  <h3>开始第一次提问</h3>
                  <p>AI 将根据关联文档中的内容回答。</p>
                </div>
              ) : (
                messages.map((message) => (
                  <article
                    className={`message ${message.role}`}
                    key={message.id}
                  >
                    <span>
                      {message.role === 'user' ? '你' : 'AI'}
                    </span>
                    <p>{message.content}</p>
                  </article>
                ))
              )}
            </div>

            {sources.length > 0 && (
              <div className="sources-panel">
                <h3>本次回答引用来源</h3>
                {sources.map((source) => (
                  <details key={source.chunk_id}>
                    <summary>
                      Chunk {source.chunk_id} · 距离{' '}
                      {source.distance.toFixed(4)}
                    </summary>
                    <p>{source.content}</p>
                  </details>
                ))}
              </div>
            )}

            <form className="chat-composer" onSubmit={handleAsk}>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="向当前知识库提问..."
                rows={3}
              />

              <button
                type="submit"
                disabled={asking || !question.trim()}
              >
                {asking ? 'AI 正在回答...' : '发送问题'}
              </button>
            </form>
          </>
        )}
      </div>
    </section>
  )
}

export default ChatPage