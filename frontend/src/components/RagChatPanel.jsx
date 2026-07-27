import React, { useState, useEffect, useRef } from 'react'
import { PipelineStepper } from './PipelineStepper'
import {
  Send,
  Upload,
  Bot,
  User,
  Database,
  Sparkles,
  Eye,
  FileText,
  X,
  Sliders,
  FileCheck,
} from 'lucide-react'

export function RagChatPanel() {
  // Ingestion & File State
  const [files, setFiles] = useState([])
  const [chunkTechnique, setChunkTechnique] = useState('semantic_chunker')
  const [retrievalTechnique, setRetrievalTechnique] = useState('dense')
  const [selectedModel, setSelectedModel] = useState('google/gemini-2.0-flash-001')
  const [sessionId, setSessionId] = useState(null)

  // Ingestion Stepper State
  const [ingestStatus, setIngestStatus] = useState('idle') // 'idle'|'parsing'|'chunking'|'embedding'|'indexing'|'complete'|'error'
  const [ingestStep, setIngestStep] = useState('')
  const [ingestMsg, setIngestMsg] = useState('')
  const [ingestProgress, setIngestProgress] = useState(0)

  // Options catalogs from backend
  const [models, setModels] = useState([])
  const [retrievers, setRetrievers] = useState([])
  const [techniques, setTechniques] = useState([])

  // Chat State
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to Multimodal RAG Studio! Select your files, choose your chunker and retriever strategies above, then click "Process & Build Qdrant Index" to get started.',
    },
  ])
  const [inputQuery, setInputQuery] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  // Context Inspector Modal State
  const [inspectorContext, setInspectorContext] = useState(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    fetch('/api/rag/models')
      .then(res => res.json())
      .then(data => setModels(data.models || []))
      .catch(console.error)

    fetch('/api/rag/retrievers')
      .then(res => res.json())
      .then(data => setRetrievers(data.retrievers || []))
      .catch(console.error)

    fetch('/api/techniques')
      .then(res => res.json())
      .then(data => {
        if (data.categories) {
          const flat = []
          Object.values(data.categories).forEach(arr => flat.push(...arr))
          setTechniques(flat)
        }
      })
      .catch(console.error)
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chatLoading])

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleRunIngestion = async () => {
    if (!files.length) return

    setIngestStatus('parsing')
    setIngestStep('parsing')
    setIngestMsg('Uploading document batch...')
    setIngestProgress(10)

    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    formData.append('chunk_technique', chunkTechnique)
    formData.append('chunk_params_json', JSON.stringify({}))

    try {
      const response = await fetch('/api/rag/pipeline-stream', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const eventStr of events) {
          if (!eventStr.trim()) continue
          const lines = eventStr.split('\n')
          let eventName = 'message'
          let dataStr = '{}'

          for (const line of lines) {
            if (line.startsWith('event:')) eventName = line.replace('event:', '').trim()
            if (line.startsWith('data:')) dataStr = line.replace('data:', '').trim()
          }

          try {
            const data = JSON.parse(dataStr)
            if (eventName === 'progress') {
              setIngestStatus(data.step)
              setIngestStep(data.step)
              setIngestMsg(data.message)
              setIngestProgress(data.progress)
            } else if (eventName === 'done') {
              setSessionId(data.session_id)
              setIngestStatus('complete')
            } else if (eventName === 'error') {
              setIngestStatus('error')
              setIngestMsg(data.message)
            }
          } catch (err) {
            console.error('SSE parse error:', err)
          }
        }
      }
    } catch (err) {
      console.error('Pipeline SSE error:', err)
      setIngestStatus('error')
      setIngestMsg(err.message)
    }
  }

  const handleSendChat = async (e) => {
    e?.preventDefault()
    if (!inputQuery.trim() || chatLoading) return

    const userText = inputQuery.trim()
    setInputQuery('')
    setMessages(prev => [...prev, { role: 'user', content: userText }])
    setChatLoading(true)

    try {
      const res = await fetch('/api/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userText,
          model_id: selectedModel,
          retrieval_technique: retrievalTechnique,
          session_id: sessionId,
          limit: 4,
        }),
      })

      if (!res.ok) throw new Error(`RAG query failed: ${res.statusText}`)
      const data = await res.json()

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          context: data.retrieved_context,
          model: data.model_used,
          retriever: data.retrieval_technique,
        },
      ])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `❌ Error: ${err.message}` },
      ])
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* ── Control Panel Card ────────────────────────────────────────── */}
      <div className="card" style={{ padding: '1.25rem 1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Sliders size={18} color="#818cf8" />
            <span>RAG Strategy & Pipeline Configuration</span>
          </h3>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Single 512d CLIP Vector Space
          </span>
        </div>

        {/* Strategy Controls Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.85rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-secondary)' }}>
              LLM Model (OpenRouter)
            </label>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
              className="select-input"
            >
              {models.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-secondary)' }}>
              Chunking Strategy (21 Available)
            </label>
            <select
              value={chunkTechnique}
              onChange={e => setChunkTechnique(e.target.value)}
              className="select-input"
            >
              {techniques.map(t => (
                <option key={t.name} value={t.name}>
                  {t.name.replace(/_/g, ' ').toUpperCase()} ({t.category})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-secondary)' }}>
              Retrieval Technique
            </label>
            <select
              value={retrievalTechnique}
              onChange={e => setRetrievalTechnique(e.target.value)}
              className="select-input"
            >
              {retrievers.map(r => (
                <option key={r.name} value={r.name}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Upload & Index Bar */}
        <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
          <label
            style={{
              flex: 1,
              minWidth: '240px',
              border: '1px dashed rgba(255, 255, 255, 0.15)',
              borderRadius: 'var(--radius-md)',
              padding: '0.7rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              cursor: 'pointer',
              background: 'rgba(15, 23, 42, 0.6)',
              fontSize: '0.875rem',
              color: 'var(--text-primary)',
              transition: 'border-color 0.2s ease',
            }}
          >
            {files.length ? <FileCheck size={18} color="#10b981" /> : <Upload size={18} color="#818cf8" />}
            <span>{files.length ? `${files.length} document(s) selected` : 'Drop or Select Files (PDF, PNG, DOCX, CSV...)'}</span>
            <input type="file" multiple onChange={handleFileChange} style={{ display: 'none' }} />
          </label>

          <button
            onClick={handleRunIngestion}
            disabled={!files.length || (ingestStatus !== 'idle' && ingestStatus !== 'complete' && ingestStatus !== 'error')}
            className="btn btn-primary"
            style={{ padding: '0.7rem 1.4rem' }}
          >
            <Database size={17} />
            <span>Process & Build Index</span>
          </button>
        </div>

        {/* Real-time Stepper Animation */}
        <PipelineStepper
          status={ingestStatus}
          step={ingestStep}
          message={ingestMsg}
          progress={ingestProgress}
        />
      </div>

      {/* ── Interactive Chat Interface ─────────────────────────────────── */}
      <div className="card" style={{ padding: '1.25rem 1.5rem', display: 'flex', flexDirection: 'column', height: '540px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Bot size={18} color="#cba6f7" />
            <span>Multimodal RAG Conversation</span>
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
            Retriever: <strong>{retrievalTechnique}</strong>
          </span>
        </div>

        {/* Chat History Container */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.4rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: '0.75rem',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                alignItems: 'flex-start',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: msg.role === 'user' ? 'linear-gradient(135deg, #6366f1, #818cf8)' : '#1e293b',
                  border: `1px solid ${msg.role === 'user' ? 'transparent' : 'rgba(255,255,255,0.1)'}`,
                  color: msg.role === 'user' ? '#ffffff' : '#cba6f7',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div style={{ maxWidth: '82%' }}>
                <div
                  style={{
                    background: msg.role === 'user' ? 'rgba(99, 102, 241, 0.14)' : 'rgba(255, 255, 255, 0.04)',
                    border: `1px solid ${msg.role === 'user' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.08)'}`,
                    borderRadius: 'var(--radius-md)',
                    padding: '0.75rem 1rem',
                    fontSize: '0.9rem',
                    lineHeight: '1.55',
                    color: 'var(--text-primary)',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>

                {/* Inspect Context Button */}
                {msg.context && msg.context.length > 0 && (
                  <button
                    onClick={() => setInspectorContext(msg.context)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#818cf8',
                      fontSize: '0.78rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      cursor: 'pointer',
                      marginTop: '0.35rem',
                      fontWeight: 500,
                    }}
                  >
                    <Eye size={13} />
                    <span>Inspect {msg.context.length} Retrieved Chunks ({msg.retriever})</span>
                  </button>
                )}
              </div>
            </div>
          ))}

          {chatLoading && (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cba6f7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={16} />
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '0.6rem 0.9rem', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <span className="pulse-dot" style={{ marginRight: '0.5rem' }} />
                Synthesizing response via OpenRouter ({selectedModel})...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Query Input Bar */}
        <form onSubmit={handleSendChat} style={{ display: 'flex', gap: '0.65rem', marginTop: '0.85rem' }}>
          <input
            type="text"
            placeholder="Ask a question based on your indexed document context..."
            value={inputQuery}
            onChange={e => setInputQuery(e.target.value)}
            className="text-input"
            style={{ flex: 1, padding: '0.65rem 0.9rem' }}
          />
          <button type="submit" disabled={!inputQuery.trim() || chatLoading} className="btn btn-primary" style={{ padding: '0.65rem 1.1rem' }}>
            <Send size={16} />
          </button>
        </form>
      </div>

      {/* ── Context Inspector Modal ────────────────────────────────────── */}
      {inspectorContext && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1.5rem',
          }}
        >
          <div
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-lg)',
              maxWidth: '720px',
              width: '100%',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
            }}
          >
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Eye color="#818cf8" size={18} />
                <span>Context Inspector — Retrieved Chunks</span>
              </h3>
              <button onClick={() => setInspectorContext(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <div style={{ padding: '1.25rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {inspectorContext.map((c, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.78rem' }}>
                    <span style={{ color: '#818cf8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <FileText size={13} />
                      {c.source_name}
                    </span>
                    <span style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#10b981', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 600 }}>
                      Score: {c.score}
                    </span>
                  </div>
                  <pre
                    style={{
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.82rem',
                      color: 'var(--text-secondary)',
                      background: 'var(--bg-input)',
                      padding: '0.65rem 0.85rem',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    {c.text}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
