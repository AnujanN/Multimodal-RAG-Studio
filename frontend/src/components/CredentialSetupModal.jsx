import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { X, Key, Database, Zap, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react'

export function CredentialSetupModal({ onDone, onSkip, isSettings = false }) {
  const { saveCredentials } = useAuth()
  const [qdrantUrl, setQdrantUrl] = useState('')
  const [qdrantKey, setQdrantKey] = useState('')
  const [openrouterKey, setOpenrouterKey] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    setError(null)

    if (!qdrantUrl || !qdrantKey || !openrouterKey) {
      setError('Please fill in all three credential fields to enable RAG.')
      return
    }

    setSaving(true)
    try {
      await saveCredentials(qdrantUrl.trim(), qdrantKey.trim(), openrouterKey.trim())
      setSaved(true)
      setTimeout(() => onDone(), 800)
    } catch (err) {
      setError(err.message || 'Failed to save credentials.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000,
        padding: '1.5rem',
      }}
    >
      <div
        className="card"
        style={{ maxWidth: '500px', width: '100%', padding: '0', overflow: 'hidden' }}
      >
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Key size={18} color="#818cf8" />
              {isSettings ? 'API Key Settings' : 'Configure Your API Keys'}
            </h3>
            <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {isSettings ? 'Update your Qdrant & OpenRouter credentials' : 'Your keys are encrypted and stored securely'}
            </p>
          </div>
          {(isSettings || onSkip) && (
            <button
              onClick={onSkip || onDone}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>
          )}
        </div>

        <form onSubmit={handleSave} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
          {/* Qdrant Section */}
          <div style={{
            background: 'rgba(245, 158, 11, 0.05)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f59e0b' }}>
                <Database size={15} /> Qdrant Cloud
              </span>
              <a
                href="https://cloud.qdrant.io"
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: '0.75rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}
              >
                Get credentials <ExternalLink size={11} />
              </a>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>
                  Cluster Endpoint URL
                </label>
                <input
                  type="url"
                  placeholder="https://xxxxx.cloud.qdrant.io:6333"
                  value={qdrantUrl}
                  onChange={e => setQdrantUrl(e.target.value)}
                  className="text-input"
                  style={{ fontSize: '0.83rem' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>
                  API Key
                </label>
                <input
                  type="password"
                  placeholder="Your Qdrant API key"
                  value={qdrantKey}
                  onChange={e => setQdrantKey(e.target.value)}
                  className="text-input"
                  style={{ fontSize: '0.83rem' }}
                />
              </div>
            </div>
          </div>

          {/* OpenRouter Section */}
          <div style={{
            background: 'rgba(99, 102, 241, 0.05)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#818cf8' }}>
                <Zap size={15} /> OpenRouter
              </span>
              <a
                href="https://openrouter.ai/keys"
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: '0.75rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}
              >
                Get API key <ExternalLink size={11} />
              </a>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-secondary)' }}>
                API Key
              </label>
              <input
                type="password"
                placeholder="sk-or-v1-..."
                value={openrouterKey}
                onChange={e => setOpenrouterKey(e.target.value)}
                className="text-input"
                style={{ fontSize: '0.83rem' }}
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.25)',
              borderRadius: '8px',
              padding: '0.6rem 0.8rem',
              fontSize: '0.82rem',
              color: '#fca5a5',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}>
              <AlertCircle size={14} /> {error}
            </div>
          )}

          {saved && (
            <div style={{
              background: 'rgba(16,185,129,0.1)',
              border: '1px solid rgba(16,185,129,0.25)',
              borderRadius: '8px',
              padding: '0.6rem 0.8rem',
              fontSize: '0.82rem',
              color: '#10b981',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}>
              <CheckCircle size={14} /> Credentials saved! RAG features are now unlocked.
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '0.65rem', marginTop: '0.25rem' }}>
            <button
              type="submit"
              disabled={saving || saved}
              className="btn btn-primary"
              style={{ flex: 1, padding: '0.7rem' }}
            >
              {saving ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="pulse-dot" /> Saving...
                </span>
              ) : saved ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle size={16} /> Saved!
                </span>
              ) : (
                'Save API Keys & Unlock RAG'
              )}
            </button>

            {!isSettings && onSkip && (
              <button
                type="button"
                onClick={onSkip}
                className="btn btn-secondary"
                style={{ padding: '0.7rem 1rem', fontSize: '0.85rem' }}
              >
                Skip for now
              </button>
            )}
          </div>

          {!isSettings && (
            <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              You can always add keys later via ⚙️ Settings. Skipping will give access to the Chunking Lab only.
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
