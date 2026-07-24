import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { BarChart3 } from 'lucide-react'

export function ChunkChart({ chunks }) {
  if (!chunks || chunks.length === 0) return null

  // Prepare chart dataset
  const data = chunks.map((chunkText, idx) => ({
    name: `#${idx + 1}`,
    size: chunkText.length,
    words: chunkText.split(/\s+/).filter(Boolean).length,
  }))

  const avgSize = Math.round(
    data.reduce((acc, curr) => acc + curr.size, 0) / data.length
  )

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload
      return (
        <div
          style={{
            background: 'rgba(18, 23, 35, 0.95)',
            border: '1px solid var(--border-color)',
            padding: '0.5rem 0.75rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.8rem',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <p style={{ fontWeight: '600', color: 'var(--accent-purple)' }}>
            Chunk {d.name}
          </p>
          <p style={{ color: 'var(--text-primary)' }}>
            Size: <strong>{d.size}</strong> chars
          </p>
          <p style={{ color: 'var(--text-muted)' }}>
            Words: <strong>{d.words}</strong>
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="glass-card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart3 size={18} color="var(--accent-cyan)" />
          Chunk Size Distribution
        </h3>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Average: <strong>{avgSize}</strong> chars
        </span>
      </div>

      <div style={{ width: '100%', height: '220px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="name"
              stroke="var(--text-muted)"
              fontSize={11}
              tickLine={false}
            />
            <YAxis
              stroke="var(--text-muted)"
              fontSize={11}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="size" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    entry.size > avgSize * 1.3
                      ? 'var(--accent-purple)'
                      : entry.size < avgSize * 0.7
                      ? 'var(--accent-cyan)'
                      : '#6366f1'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
