import React, { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2, Sparkles } from 'lucide-react'

export function FileUpload({ onFileUpload, uploading, uploadInfo }) {
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileUpload(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0])
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-purple)' : 'rgba(255, 255, 255, 0.15)'}`,
          background: dragActive ? 'rgba(168, 85, 247, 0.08)' : 'rgba(0, 0, 0, 0.2)',
          borderRadius: 'var(--radius-md)',
          padding: '1.5rem',
          textAlign: 'center',
          cursor: uploading ? 'wait' : 'pointer',
          transition: 'all 0.2s ease',
          position: 'relative',
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md,.csv,.json,.html,.png,.jpg,.jpeg,.tiff"
          onChange={handleChange}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        {uploading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <Loader2 size={32} color="var(--accent-purple)" className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Parsing document with <strong>Docling + RapidOCR</strong>...
            </p>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Extracting structured Markdown & preserving table layouts
            </span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ background: 'rgba(168, 85, 247, 0.15)', padding: '0.6rem', borderRadius: '50%', color: 'var(--accent-purple)' }}>
              <UploadCloud size={24} />
            </div>
            <div>
              <p style={{ fontSize: '0.95rem', fontWeight: '500', color: 'var(--text-primary)' }}>
                Drag & drop document or <span style={{ color: 'var(--accent-purple)', textDecoration: 'underline' }}>browse</span>
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Supports 9 formats: PDF (text & scanned), DOCX, TXT, MD, CSV, JSON, HTML, PNG, JPG
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Upload Status Badge */}
      {uploadInfo && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-md)', fontSize: '0.8rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-green)' }}>
            <CheckCircle size={15} />
            <span>
              <strong>{uploadInfo.filename}</strong> ({uploadInfo.characterCount.toLocaleString()} chars)
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
            <Sparkles size={11} color="var(--accent-amber)" /> {uploadInfo.parserUsed}
          </span>
        </div>
      )}
    </div>
  )
}
