import React from 'react'
import { FileText, Edit3, Upload, Play, RefreshCw } from 'lucide-react'
import { FileUpload } from './FileUpload'
import { formatNumber } from '../utils/formatters'

export function InputPanel({
  sourceType,
  setSourceType,
  presets,
  selectedPreset,
  onPresetChange,
  inputText,
  setInputText,
  uploadInfo,
  onFileUpload,
  uploading,
  loading,
  onProcessText,
}) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Source Selector Tabs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileText size={18} color="var(--accent-cyan)" />
          Input Document Text
        </h3>

        <div style={{ display: 'flex', background: 'rgba(0,0,0,0.3)', padding: '0.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setSourceType('preset')}
            style={{
              background: sourceType === 'preset' ? 'var(--brand-gradient)' : 'transparent',
              color: sourceType === 'preset' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              transition: 'all 0.15s ease',
            }}
          >
            <FileText size={13} /> Preset
          </button>
          <button
            onClick={() => setSourceType('upload')}
            style={{
              background: sourceType === 'upload' ? 'var(--brand-gradient)' : 'transparent',
              color: sourceType === 'upload' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              transition: 'all 0.15s ease',
            }}
          >
            <Upload size={13} /> Upload File
          </button>
          <button
            onClick={() => setSourceType('custom')}
            style={{
              background: sourceType === 'custom' ? 'var(--brand-gradient)' : 'transparent',
              color: sourceType === 'custom' ? '#fff' : 'var(--text-secondary)',
              border: 'none',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              transition: 'all 0.15s ease',
            }}
          >
            <Edit3 size={13} /> Custom Text
          </button>
        </div>
      </div>

      {/* Preset Dropdown Controls */}
      {sourceType === 'preset' && (
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {presets.map((p) => (
            <button
              key={p.name}
              onClick={() => onPresetChange(p.name)}
              className="btn-secondary"
              style={{
                background: selectedPreset === p.name ? 'rgba(168, 85, 247, 0.2)' : 'rgba(255,255,255,0.03)',
                borderColor: selectedPreset === p.name ? 'var(--accent-purple)' : 'var(--border-color)',
                color: selectedPreset === p.name ? '#fff' : 'var(--text-secondary)',
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      )}

      {/* File Upload Dropzone */}
      {sourceType === 'upload' && (
        <FileUpload onFileUpload={onFileUpload} uploading={uploading} uploadInfo={uploadInfo} />
      )}

      {/* Editable Text Area */}
      <div style={{ position: 'relative' }}>
        <textarea
          className="input-textarea"
          rows={12}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste or type text here to chunk..."
        />

        {/* Char Counter & Quick Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span>
            {formatNumber(inputText.length)} characters | {formatNumber(inputText.split(/\s+/).filter(Boolean).length)} words
          </span>
          {inputText && (
            <button
              onClick={() => setInputText('')}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.75rem' }}
            >
              Clear Text
            </button>
          )}
        </div>
      </div>

      {/* Process Text CTA Button */}
      <button
        onClick={onProcessText}
        disabled={loading || !inputText.trim()}
        className="btn-primary"
        style={{ width: '100%', padding: '0.85rem', fontSize: '1.05rem', marginTop: '0.25rem' }}
      >
        {loading ? (
          <>
            <RefreshCw size={18} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
            Processing Text...
          </>
        ) : (
          <>
            <Play size={18} />
            Process Text
          </>
        )}
      </button>
    </div>
  )
}
