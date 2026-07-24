import React from 'react'
import { Sliders, HelpCircle, CheckCircle2 } from 'lucide-react'
import { formatTechniqueName } from '../utils/formatters'

export function TechniqueSelector({ techniques, selectedTechnique, onTechniqueChange, currentInfo }) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sliders size={18} color="var(--accent-purple)" />
          Chunking Technique
        </h3>
        {currentInfo?.category && (
          <span className={`badge badge-${currentInfo.category}`}>
            {currentInfo.category.replace('_', ' ')}
          </span>
        )}
      </div>

      {/* Select Dropdown */}
      <div style={{ marginBottom: '1rem' }}>
        <select
          className="input-select"
          value={selectedTechnique}
          onChange={(e) => onTechniqueChange(e.target.value)}
          style={{ fontSize: '0.95rem', fontWeight: '500' }}
        >
          <optgroup label="⚡ Basic Techniques (6)">
            {(techniques.basic || []).map((t) => (
              <option key={t.name} value={t.name}>
                {formatTechniqueName(t.name)}
              </option>
            ))}
          </optgroup>
          <optgroup label="🚀 Advanced Techniques (8)">
            {(techniques.advanced || []).map((t) => (
              <option key={t.name} value={t.name}>
                {formatTechniqueName(t.name)}
              </option>
            ))}
          </optgroup>
          <optgroup label="🧠 AI-Powered Techniques (7)">
            {(techniques.ai_powered || []).map((t) => (
              <option key={t.name} value={t.name}>
                {formatTechniqueName(t.name)}
              </option>
            ))}
          </optgroup>
        </select>
      </div>

      {/* Description & Use Cases Display */}
      {currentInfo && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.05)' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            {currentInfo.description}
          </p>

          {currentInfo.use_cases && currentInfo.use_cases.length > 0 && (
            <div>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: '600', marginBottom: '0.4rem', letterSpacing: '0.05em' }}>
                Recommended Use Cases
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {currentInfo.use_cases.map((uc, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                    <CheckCircle2 size={13} color="var(--accent-green)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span>{uc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
