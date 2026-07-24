import React, { useState } from 'react'
import { Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'
import { formatNumber } from '../utils/formatters'

export function ChunkCard({ index, text, totalChunks }) {
  const [copied, setCopied] = useState(false)
  const [expanded, setExpanded] = useState(true)

  const handleCopy = (e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const wordCount = text.split(/\s+/).filter(Boolean).length

  return (
    <div
      className="glass-card"
      style={{
        padding: '1rem',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(18, 23, 35, 0.7)',
      }}
    >
      {/* Chunk Header Bar */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          userSelect: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span
            style={{
              background: 'var(--brand-gradient)',
              color: '#fff',
              fontWeight: '700',
              fontSize: '0.8rem',
              padding: '0.2rem 0.6rem',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-heading)',
            }}
          >
            Chunk #{index + 1}
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {formatNumber(text.length)} chars | {wordCount} words
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={handleCopy}
            title="Copy chunk text"
            style={{
              background: copied ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${copied ? 'var(--accent-green)' : 'var(--border-color)'}`,
              color: copied ? 'var(--accent-green)' : 'var(--text-secondary)',
              padding: '0.3rem 0.6rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
            }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
            }}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded Content View */}
      {expanded && (
        <div
          style={{
            marginTop: '0.75rem',
            paddingTop: '0.75rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <pre
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.83rem',
              lineHeight: '1.5',
              color: 'var(--text-primary)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              background: 'rgba(0, 0, 0, 0.25)',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              maxHeight: '300px',
              overflowY: 'auto',
            }}
          >
            {text}
          </pre>
        </div>
      )}
    </div>
  )
}
