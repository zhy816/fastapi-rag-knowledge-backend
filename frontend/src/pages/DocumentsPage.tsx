import axios from 'axios'
import { useCallback, useEffect, useState, type FormEvent } from 'react'

import apiClient from '../api/client'
import type { Document } from '../types'

function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [processingId, setProcessingId] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadDocuments = useCallback(async () => {
    try {
      const response = await apiClient.get<Document[]>('/documents/')
      setDocuments(response.data)
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '文档列表加载失败')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadDocuments()
  }, [loadDocuments])

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!file) {
      setError('请先选择文件')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      await apiClient.post('/documents/upload', formData)
      setMessage('文档上传成功')
      setFile(null)
      await loadDocuments()
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '文档上传失败')
      }
    } finally {
      setUploading(false)
    }
  }

  async function processDocument(
    documentId: number,
    action: 'parse' | 'vectorize',
  ) {
    setProcessingId(documentId)
    setError('')
    setMessage('')

    try {
      await apiClient.post(`/documents/${documentId}/${action}`)
      setMessage(action === 'parse' ? '文档解析成功' : '文档向量化成功')
      await loadDocuments()
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(requestError.response?.data?.detail ?? '文档处理失败')
      }
    } finally {
      setProcessingId(null)
    }
  }

  return (
    <section className="documents-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">DOCUMENTS</p>
          <h2>文档管理</h2>
          <p>支持 PDF、DOCX 和 TXT 文件。</p>
        </div>

        <form className="upload-form" onSubmit={handleUpload}>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null)
            }}
          />

          <button type="submit" disabled={uploading}>
            {uploading ? '上传中...' : '上传文档'}
          </button>
        </form>
      </div>

      {message && <p className="status-message success">{message}</p>}
      {error && <p className="status-message error">{error}</p>}

      {loading ? (
        <p className="empty-state">正在加载文档...</p>
      ) : documents.length === 0 ? (
        <p className="empty-state">还没有文档，请先上传一份资料。</p>
      ) : (
        <div className="document-list">
          {documents.map((document) => (
            <article className="document-card" key={document.id}>
              <div className="file-icon">
                {document.file_type.toUpperCase()}
              </div>

              <div className="document-info">
                <h3>{document.filename}</h3>
                <p>
                  文档 ID：{document.id} · 状态：{document.status}
                </p>
              </div>

              <div className="document-actions">
                <button
                  type="button"
                  disabled={processingId === document.id}
                  onClick={() => void processDocument(document.id, 'parse')}
                >
                  解析
                </button>

                <button
                  type="button"
                  className="primary-button"
                  disabled={processingId === document.id}
                  onClick={() =>
                    void processDocument(document.id, 'vectorize')
                  }
                >
                  向量化
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default DocumentsPage