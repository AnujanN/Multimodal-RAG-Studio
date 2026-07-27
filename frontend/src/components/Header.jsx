import React from 'react'
import { Layers, Sparkles, Cpu, ShieldCheck } from 'lucide-react'

export function Header() {
  return (
    <header className="card" style={{ padding: '1.25rem 1.75rem', position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              padding: '0.65rem',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
            }}
          >
            <Layers size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h1 style={{ fontSize: '1.45rem', letterSpacing: '-0.02em', fontWeight: 700 }}>
                Chunking Strategies & Multimodal RAG Studio
              </h1>
              <span className="badge badge-basic" style={{ fontSize: '0.7rem' }}>
                <Sparkles size={11} style={{ marginRight: '3px' }} /> v0.1.0
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.15rem' }}>
              High-precision RAG playground featuring 21 chunking strategies, Qdrant Cloud 512d CLIP vectors, and OpenRouter LLMs.
            </p>
          </div>
        </div>

        {/* System Badges */}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.1)', padding: '0.3rem 0.75rem', borderRadius: '9999px', border: '1px solid rgba(16, 185, 129, 0.2)', fontWeight: 500 }}>
            <ShieldCheck size={14} /> Qdrant Cloud Ready
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Cpu size={14} color="#818cf8" /> Docling OCR + FastEmbed
          </div>
        </div>
      </div>
    </header>
  )
}
