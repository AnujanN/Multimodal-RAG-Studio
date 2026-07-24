import React from 'react'
import { Layers, Sparkles, Cpu, BookOpen } from 'lucide-react'

export function Header() {
  return (
    <header className="glass-card" style={{ padding: '1.5rem 2rem', position: 'relative', overflow: 'hidden' }}>
      {/* Background Ambient Glow */}
      <div
        style={{
          position: 'absolute',
          top: '-50%',
          right: '-10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none',
        }}
      />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              background: 'var(--brand-gradient)',
              padding: '0.75rem',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            <Layers size={28} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.75rem', letterSpacing: '-0.02em' }}>
                Chunking Strategy Playground
              </h1>
              <span className="badge badge-ai_powered" style={{ fontSize: '0.75rem' }}>
                <Sparkles size={12} style={{ marginRight: '4px' }} /> 21 Techniques
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
              Interactive testbed for basic, advanced, and AI-powered text chunking strategies for building high-precision RAG systems.
            </p>
          </div>
        </div>

        {/* Feature Badges */}
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Cpu size={14} color="var(--accent-purple)" /> FastEmbed & Docling OCR
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <BookOpen size={14} color="var(--accent-cyan)" /> 9 Upload Formats
          </div>
        </div>
      </div>
    </header>
  )
}
