import React from 'react'
import { FileText, Scissors, Cpu, Database, CheckCircle2, AlertCircle } from 'lucide-react'

export function PipelineStepper({ status, step, message, progress }) {
  if (status === 'idle') return null

  const steps = [
    { key: 'parsing', label: 'Parsing', icon: FileText, desc: 'Extracting text & OCR' },
    { key: 'chunking', label: 'Chunking', icon: Scissors, desc: 'Splitting document text' },
    { key: 'embedding', label: 'Embedding', icon: Cpu, desc: '512d CLIP vector generation' },
    { key: 'indexing', label: 'Qdrant Index', icon: Database, desc: 'Vector database storing' },
  ]

  const getStepStatus = (stepKey) => {
    if (status === 'complete') return 'completed'
    if (status === 'error') return 'error'

    const stepOrder = ['parsing', 'chunking', 'embedding', 'indexing', 'complete']
    const currentIndex = stepOrder.indexOf(step)
    const thisIndex = stepOrder.indexOf(stepKey)

    if (thisIndex < currentIndex) return 'completed'
    if (thisIndex === currentIndex) return 'active'
    return 'pending'
  }

  return (
    <div
      style={{
        background: 'var(--bg-secondary, #1e1e2e)',
        border: '1px solid var(--border-color, #313244)',
        borderRadius: 'var(--radius-lg, 12px)',
        padding: '1.25rem 1.5rem',
        marginTop: '1rem',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary, #cdd6f4)' }}>
          Real-Time RAG Ingestion Pipeline
        </h4>
        <span style={{ fontSize: '0.8rem', color: 'var(--accent-color, #89b4fa)', fontWeight: 600 }}>
          {progress}%
        </span>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          width: '100%',
          height: '6px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '3px',
          overflow: 'hidden',
          marginBottom: '1.25rem',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${progress}%`,
            background: status === 'error' ? '#f38ba8' : 'linear-gradient(90deg, #89b4fa, #cba6f7)',
            transition: 'width 0.4s ease-in-out',
          }}
        />
      </div>

      {/* Stepper Steps */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
        {steps.map((s) => {
          const st = getStepStatus(s.key)
          const Icon = s.icon

          let iconBg = 'rgba(255, 255, 255, 0.05)'
          let iconColor = 'var(--text-muted, #a6adc8)'
          let borderColor = 'transparent'

          if (st === 'completed') {
            iconBg = 'rgba(166, 227, 161, 0.15)'
            iconColor = '#a6e3a1'
            borderColor = 'rgba(166, 227, 161, 0.3)'
          } else if (st === 'active') {
            iconBg = 'rgba(137, 180, 250, 0.2)'
            iconColor = '#89b4fa'
            borderColor = '#89b4fa'
          } else if (st === 'error') {
            iconBg = 'rgba(243, 139, 168, 0.15)'
            iconColor = '#f38ba8'
            borderColor = 'rgba(243, 139, 168, 0.3)'
          }

          return (
            <div
              key={s.key}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                padding: '0.75rem 0.5rem',
                borderRadius: '8px',
                background: st === 'active' ? 'rgba(137, 180, 250, 0.05)' : 'transparent',
                border: `1px solid ${borderColor}`,
                transition: 'all 0.3s ease',
              }}
            >
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  background: iconBg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '0.5rem',
                  color: iconColor,
                }}
              >
                {st === 'completed' ? <CheckCircle2 size={20} /> : <Icon size={18} />}
              </div>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: st === 'pending' ? '#6c7086' : '#cdd6f4' }}>
                {s.label}
              </span>
              <span style={{ fontSize: '0.75rem', color: '#a6adc8', marginTop: '0.2rem' }}>{s.desc}</span>
            </div>
          )
        })}
      </div>

      {/* Message Output */}
      {message && (
        <div
          style={{
            marginTop: '1rem',
            padding: '0.6rem 0.8rem',
            background: status === 'error' ? 'rgba(243, 139, 168, 0.1)' : 'rgba(255, 255, 255, 0.03)',
            borderRadius: '6px',
            fontSize: '0.85rem',
            color: status === 'error' ? '#f38ba8' : 'var(--text-secondary, #bac2de)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          {status === 'error' ? <AlertCircle size={16} /> : <span className="pulse-dot" />}
          <span>{message}</span>
        </div>
      )}
    </div>
  )
}
