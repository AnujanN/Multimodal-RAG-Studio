import React from 'react'
import { Layers, Cpu, Settings, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export function Header({ onOpenSettings }) {
  const { user, logout, credStatus } = useAuth()

  // Build user initials for avatar
  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.[0]?.toUpperCase() || '?'

  return (
    <header className="card" style={{ padding: '1rem 1.5rem', position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        {/* Left: Logo + Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              padding: '0.6rem',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
            }}
          >
            <Layers size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', letterSpacing: '-0.02em', fontWeight: 700, margin: 0 }}>
              Chunking & RAG Studio
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '0.1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Cpu size={12} color="#818cf8" />
              Docling OCR · FastEmbed CLIP 512d · Qdrant Cloud · OpenRouter
            </p>
          </div>
        </div>

        {/* Right: Cred Status + Settings + User + Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {/* Credential status badge */}
          {credStatus !== null && (
            <div style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '0.25rem 0.65rem',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: credStatus.configured
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(245, 158, 11, 0.1)',
              color: credStatus.configured ? '#10b981' : '#f59e0b',
              border: `1px solid ${credStatus.configured ? 'rgba(16,185,129,0.25)' : 'rgba(245,158,11,0.25)'}`,
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
              {credStatus.is_admin ? 'Admin · .env Keys' : credStatus.configured ? 'RAG Ready' : 'Keys Missing'}
            </div>
          )}

          {/* Settings button */}
          {!credStatus?.is_admin && (
            <button
              onClick={onOpenSettings}
              title="API Key Settings"
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '0.45rem 0.65rem',
                cursor: 'pointer',
                color: 'var(--text-secondary)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 500,
                fontFamily: 'var(--font-body)',
                transition: 'all 0.15s ease',
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = '#818cf8'; e.currentTarget.style.color = '#818cf8' }}
              onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.color = 'var(--text-secondary)' }}
            >
              <Settings size={15} /> Settings
            </button>
          )}

          {/* User avatar + email */}
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: 'var(--font-heading)',
                fontWeight: 700,
                fontSize: '0.75rem',
                flexShrink: 0,
              }}>
                {initials}
              </div>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.full_name || user.email}
              </span>
            </div>
          )}

          {/* Logout */}
          <button
            onClick={logout}
            title="Sign Out"
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '0.45rem 0.65rem',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.15s ease',
            }}
            onMouseOver={e => { e.currentTarget.style.borderColor = '#ef4444'; e.currentTarget.style.color = '#ef4444' }}
            onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.color = 'var(--text-muted)' }}
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </header>
  )
}
