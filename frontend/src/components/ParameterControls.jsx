import React from 'react'
import { Settings2 } from 'lucide-react'

export function ParameterControls({ currentInfo, parameters, onParameterChange }) {
  if (!currentInfo || !currentInfo.parameters || currentInfo.parameters.length === 0) {
    return null
  }

  const handleChange = (paramName, value) => {
    onParameterChange({
      ...parameters,
      [paramName]: value,
    })
  }

  return (
    <div className="glass-card" style={{ padding: '1.25rem' }}>
      <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Settings2 size={18} color="var(--accent-amber)" />
        Technique Parameters
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {currentInfo.parameters.map((param) => {
          const val = parameters[param.name] !== undefined ? parameters[param.name] : param.default

          return (
            <div key={param.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: '500', color: 'var(--text-primary)' }}>
                  {param.name}
                </label>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-purple)', fontFamily: 'var(--font-mono)', fontWeight: '600' }}>
                  {String(val)}
                </span>
              </div>

              {/* Integer / Float Slider + Number Input */}
              {(param.type === 'int' || param.type === 'float') && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <input
                    type="range"
                    min={param.min ?? 0}
                    max={param.max ?? 100}
                    step={param.type === 'float' ? 0.05 : 1}
                    value={val}
                    onChange={(e) =>
                      handleChange(
                        param.name,
                        param.type === 'float' ? parseFloat(e.target.value) : parseInt(e.target.value, 10)
                      )
                    }
                    style={{ flex: 1, accentColor: 'var(--accent-purple)', cursor: 'pointer' }}
                  />
                  <input
                    type="number"
                    min={param.min ?? 0}
                    max={param.max ?? 100}
                    step={param.type === 'float' ? 0.05 : 1}
                    value={val}
                    onChange={(e) =>
                      handleChange(
                        param.name,
                        param.type === 'float' ? parseFloat(e.target.value) : parseInt(e.target.value, 10)
                      )
                    }
                    className="input-text"
                    style={{ width: '70px', padding: '0.3rem 0.5rem', fontSize: '0.8rem', textAlign: 'center' }}
                  />
                </div>
              )}

              {/* Select Dropdown */}
              {param.type === 'select' && param.options && (
                <select
                  className="input-select"
                  value={val}
                  onChange={(e) => handleChange(param.name, e.target.value)}
                  style={{ padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
                >
                  {param.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              )}

              {/* String Input */}
              {param.type === 'str' && (
                <input
                  type="text"
                  className="input-text"
                  value={val}
                  onChange={(e) => handleChange(param.name, e.target.value)}
                  style={{ padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
                />
              )}

              {/* Multiselect Tags (Entity types) */}
              {param.type === 'multiselect' && param.options && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {param.options.map((opt) => {
                    const selected = Array.isArray(val) && val.includes(opt)
                    return (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => {
                          const currentArr = Array.isArray(val) ? val : []
                          const nextArr = selected
                            ? currentArr.filter((item) => item !== opt)
                            : [...currentArr, opt]
                          handleChange(param.name, nextArr)
                        }}
                        style={{
                          background: selected ? 'rgba(168, 85, 247, 0.25)' : 'rgba(255,255,255,0.05)',
                          border: `1px solid ${selected ? 'var(--accent-purple)' : 'var(--border-color)'}`,
                          color: selected ? '#fff' : 'var(--text-muted)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                        }}
                      >
                        {selected ? '✓ ' : ''}{opt}
                      </button>
                    )
                  })}
                </div>
              )}

              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {param.description}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
