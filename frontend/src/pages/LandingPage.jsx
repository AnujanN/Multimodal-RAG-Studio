import React from 'react'
import { Layers, Scissors, Database, Brain, Zap, ShieldCheck, ArrowRight, Sparkles } from 'lucide-react'

const features = [
  {
    icon: <Scissors size={22} color="#818cf8" />,
    title: '21 Chunking Strategies',
    desc: 'Basic, Advanced, and AI-Powered text chunking techniques for building high-precision RAG pipelines.',
    badge: 'Lab',
    badgeColor: '#818cf8',
  },
  {
    icon: <Brain size={22} color="#10b981" />,
    title: 'Docling OCR Parsing',
    desc: 'Parse PDFs (scanned/text), DOCX, PNG, JPG, CSV, JSON, HTML, TXT — with layout preservation.',
    badge: '9 Formats',
    badgeColor: '#10b981',
  },
  {
    icon: <Database size={22} color="#f59e0b" />,
    title: 'Qdrant Cloud Vector DB',
    desc: 'Instantly index and retrieve 512d CLIP embeddings in your own isolated Qdrant collection.',
    badge: 'Cloud',
    badgeColor: '#f59e0b',
  },
  {
    icon: <Sparkles size={22} color="#a855f7" />,
    title: 'OpenRouter LLMs',
    desc: 'Choose from Gemini 2.0 Flash, GPT-4o Mini, Llama 3.3 70B, Claude Haiku for answer synthesis.',
    badge: '4 Models',
    badgeColor: '#a855f7',
  },
  {
    icon: <Zap size={22} color="#06b6d4" />,
    title: 'Unified CLIP Embeddings',
    desc: 'Both text chunks and raw images share a single 512d CLIP vector space for cross-modal retrieval.',
    badge: '512d',
    badgeColor: '#06b6d4',
  },
  {
    icon: <ShieldCheck size={22} color="#ef4444" />,
    title: '4 Retrieval Strategies',
    desc: 'Dense Vector, Hybrid BM25+Dense, Multi-Query LLM Expansion, and Parent-Child Contextual Retrieval.',
    badge: 'RAG',
    badgeColor: '#ef4444',
  },
]

export function LandingPage({ onLoginClick, onSignupClick }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* ── Navbar ── */}
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        borderBottom: '1px solid var(--border-color)',
        position: 'sticky',
        top: 0,
        background: 'rgba(11, 15, 23, 0.92)',
        backdropFilter: 'blur(12px)',
        zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', padding: '0.5rem', borderRadius: '8px', display: 'flex' }}>
            <Layers size={20} color="#fff" />
          </div>
          <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            RAG Studio
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={onLoginClick}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              padding: '0.5rem 1.1rem',
              borderRadius: '8px',
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseOver={e => { e.target.style.borderColor = '#818cf8'; e.target.style.color = '#818cf8' }}
            onMouseOut={e => { e.target.style.borderColor = 'var(--border-color)'; e.target.style.color = 'var(--text-primary)' }}
          >
            Log In
          </button>
          <button
            onClick={onSignupClick}
            className="btn btn-primary"
            style={{ padding: '0.5rem 1.1rem', fontSize: '0.88rem' }}
          >
            Sign Up Free
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem 2rem', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '9999px',
          padding: '0.3rem 0.9rem',
          fontSize: '0.78rem',
          fontWeight: 600,
          color: '#818cf8',
          marginBottom: '1.5rem',
          letterSpacing: '0.04em',
        }}>
          <Sparkles size={13} />
          MULTIMODAL RAG PLAYGROUND
        </div>

        <h1 style={{
          fontFamily: 'var(--font-heading)',
          fontSize: 'clamp(2rem, 5vw, 3.5rem)',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          lineHeight: 1.1,
          maxWidth: '700px',
          margin: '0 0 1.25rem 0',
        }}>
          Chunking Strategies &
          <span style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            {' '}RAG Studio
          </span>
        </h1>

        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '1.1rem',
          maxWidth: '540px',
          lineHeight: 1.65,
          marginBottom: '2.5rem',
        }}>
          An interactive playground for building and testing multimodal RAG systems. Upload your own documents, choose chunking & retrieval strategies, and get AI-powered answers — using your own API keys.
        </p>

        <div style={{ display: 'flex', gap: '0.85rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button
            onClick={onSignupClick}
            className="btn btn-primary"
            style={{ padding: '0.75rem 1.8rem', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            Get Started Free <ArrowRight size={18} />
          </button>
          <button
            onClick={onLoginClick}
            className="btn btn-secondary"
            style={{ padding: '0.75rem 1.8rem', fontSize: '1rem' }}
          >
            Sign In
          </button>
        </div>

        {/* ── Features Grid ── */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1rem',
          maxWidth: '960px',
          width: '100%',
          marginTop: '4rem',
          textAlign: 'left',
        }}>
          {features.map((f, i) => (
            <div
              key={i}
              className="card"
              style={{ padding: '1.25rem', transition: 'transform 0.2s ease, box-shadow 0.2s ease' }}
              onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 16px 40px -10px rgba(0,0,0,0.5)' }}
              onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '8px', padding: '0.5rem', display: 'flex' }}>
                  {f.icon}
                </div>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.15rem 0.55rem',
                  borderRadius: '9999px',
                  background: `${f.badgeColor}18`,
                  color: f.badgeColor,
                  border: `1px solid ${f.badgeColor}30`,
                  letterSpacing: '0.05em',
                }}>
                  {f.badge}
                </span>
              </div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.4rem' }}>{f.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '3rem' }}>
          Bring your own Qdrant Cloud & OpenRouter API keys — your data stays in your own cluster.
        </p>
      </main>
    </div>
  )
}
