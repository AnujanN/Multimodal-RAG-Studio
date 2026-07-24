import React, { useState, useEffect, useRef } from 'react'
import { PipelineStepper } from './PipelineStepper'
import {
  Send,
  Upload,
  Bot,
  User,
  Database,
  Layers,
  Sparkles,
  Eye,
  FileText,
  CheckCircle2,
  X,
  HelpCircle,
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
      content: 'Hello! Upload your documents or diagrams above, pick a chunking & retrieval method, then ask me anything!',
    },
  ])
  const [inputQuery, setInputQuery] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  // Context Inspector Modal State
  const [inspectorContext, setInspectorContext] = useState(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    // Fetch models & retrievers from backend
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

  // Handle File Selection
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  // Run Ingestion Pipeline via Server-Sent Events (SSE)
  const handleRunIngestion = async () => {
    if (!files.length) return

    setIngestStatus('parsing')
    setIngestStep('parsing')
    setIngestMsg('Uploading files...')
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
            console.error('SSE JSON parse error:', err)
          }
        }
      }
    } catch (err) {
      console.error('Pipeline SSE error:', err)
      setIngestStatus('error')
      setIngestMsg(err.message)
    }
  }

  // Handle Send Chat Query
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* ── Config & Upload Control Panel ────────────────────────────────── */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
          <Sparkles color="#89b4fa" size={20} />
          <span>Multimodal RAG Setup & Controls</span>
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          {/* OpenRouter Model Selection */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: '#cdd6f4' }}>
              🤖 OpenRouter LLM Model
            </label>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
              className="select-input"
              style={{ width: '100%' }}
            >
              {models.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.provider})
                </option>
              ))}
            </select>
          </div>

          {/* Chunking Method Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: '#cdd6f4' }}>
              ✂️ Chunking Strategy (21 Available)
            </label>
            <select
              value={chunkTechnique}
              onChange={e => setChunkTechnique(e.target.value)}
              className="select-input"
              style={{ width: '100%' }}
            >
              {techniques.map(t => (
                <option key={t.name} value={t.name}>
                  {t.name.replace('_', ' ').toUpperCase()} ({t.category})
                </option>
              ))}
            </select>
          </div>

          {/* Retrieval Method Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.4rem', color: '#cdd6f4' }}>
              🔍 Retrieval Strategy
            </label>
            <select
              value={retrievalTechnique}
              onChange={e => setRetrievalTechnique(e.target.value)}
              className="select-input"
              style={{ width: '100%' }}
            >
              {retrievers.map(r => (
                <option key={r.name} value={r.name}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Multi-File Upload Box */}
        <div style={{ marginTop: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <label
            style={{
              flex: 1,
              minWidth: '240px',
              border: '2px dashed var(--border-color, #313244)',
              borderRadius: 'var(--radius-md, 8px)',
              padding: '0.8rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              cursor: 'pointer',
              background: 'rgba(255, 255, 255, 0.02)',
              fontSize: '0.9rem',
              color: '#cdd6f4',
            }}
          >
            <Upload size={18} color="#89b4fa" />
            <span>{files.length ? `${files.length} file(s) selected` : 'Select Documents / Images (PDF, PNG, DOCX...)'}</span>
            <input type="file" multiple onChange={handleFileChange} style={{ display: 'none' }} />
          </label>

          <button
            onClick={handleRunIngestion}
            disabled={!files.length || (ingestStatus !== 'idle' && ingestStatus !== 'complete' && ingestStatus !== 'error')}
            className="btn btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.8rem 1.5rem' }}
          >
            <Database size={18} />
            <span>Process & Build Qdrant Index</span>
          </button>
        </div>

        {/* Live SSE Stepper */}
        <PipelineStepper
          status={ingestStatus}
          step={ingestStep}
          message={ingestMsg}
          progress={ingestProgress}
        />
      </div>

      {/* ── RAG Chat Window ──────────────────────────────────────────────── */}
      <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '520px' }}>
        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot color="#cba6f7" size={20} />
          <span>Interactive RAG QA Chat</span>
        </h3>

        {/* Messages Stream */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: '0.75rem',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  background: msg.role === 'user' ? '#89b4fa' : '#cba6f7',
                  color: '#11111b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>

              <div style={{ maxWidth: '80%' }}>
                <div
                  style={{
                    background: msg.role === 'user' ? 'rgba(137, 180, 250, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    border: `1px solid ${msg.role === 'user' ? 'rgba(137, 180, 250, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                    borderRadius: '12px',
                    padding: '0.85rem 1.1rem',
                    fontSize: '0.92rem',
                    lineHeight: '1.5',
                    color: '#cdd6f4',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>

                {/* Retrieved Context Inspector Button */}
                {msg.context && msg.context.length > 0 && (
                  <button
                    onClick={() => setInspectorContext(msg.context)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#89b4fa',
                      fontSize: '0.8rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      cursor: 'pointer',
                      marginTop: '0.4rem',
                    }}
                  >
                    <Eye size={14} />
                    <span>Inspect {msg.context.length} Retrieved Context Chunks ({msg.retriever})</span>
                  </button>
                )}
              </div>
            </div>
          ))}

          {chatLoading && (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: '#cba6f7', color: '#11111b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={18} />
              </div>
              <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '0.6rem 1rem', borderRadius: '12px', fontSize: '0.85rem', color: '#a6adc8' }}>
                Searching Qdrant & synthesizing answer via OpenRouter...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendChat} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
          <input
            type="text"
            placeholder="Ask a question about your indexed documents..."
            value={inputQuery}
            onChange={e => setInputQuery(e.target.value)}
            className="text-input"
            style={{ flex: 1, padding: '0.75rem 1rem' }}
          />
          <button type="submit" disabled={!inputQuery.trim() || chatLoading} className="btn btn-primary" style={{ padding: '0.75rem 1.25rem' }}>
            <Send size={18} />
          </button>
        </form>
      </div>

      {/* ── Context Inspector Modal ────────────────────────────────────────── */}
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
              background: 'var(--bg-secondary, #1e1e2e)',
              border: '1px solid var(--border-color, #313244)',
              borderRadius: '16px',
              maxWidth: '750px',
              width: '100%',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
            }}
          >
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color, #313244)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#cdd6f4' }}>
                <Eye color="#89b4fa" size={20} />
                <span>Context Inspector (Retrieved Chunks)</span>
              </h3>
              <button onClick={() => setInspectorContext(null)} style={{ background: 'none', border: 'none', color: '#a6adc8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {inspectorContext.map((c, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '8px',
                    padding: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                    <span style={{ color: '#89b4fa', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <FileText size={14} />
                      {c.source_name}
                    </span>
                    <span style={{ background: 'rgba(166, 227, 161, 0.15)', color: '#a6e3a1', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>
                      Match Score: {c.score}
                    </span>
                  </div>
                  <pre
                    style={{
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'monospace',
                      fontSize: '0.85rem',
                      color: '#bac2de',
                      background: 'rgba(0, 0, 0, 0.2)',
                      padding: '0.75rem',
                      borderRadius: '6px',
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
