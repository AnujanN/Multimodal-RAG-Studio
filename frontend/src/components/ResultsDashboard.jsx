import React from 'react'
import { Layers, Clock, FileCheck, Type, Sparkles } from 'lucide-react'
import { formatNumber, formatTime, formatTechniqueName } from '../utils/formatters'
import { ChunkChart } from './ChunkChart'
import { ChunkCard } from './ChunkCard'

export function ResultsDashboard({ result }) {
  if (!result) return null

  const { stats, chunks, processing_time_ms, technique, source_type, source_name } = result

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} className="animate-fade-in">
      {/* Result Header Badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={20} color="var(--accent-purple)" />
          <h2 style={{ fontSize: '1.3rem' }}>
            Chunking Results — <span style={{ color: 'var(--accent-purple)' }}>{formatTechniqueName(technique)}</span>
          </h2>
        </div>

        {source_name && (
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-sm)' }}>
            Source: <strong>{source_name}</strong> ({source_type})
          </span>
        )}
      </div>

      {/* 4 Key Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
        <div className="glass-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: 'rgba(59, 130, 246, 0.15)', padding: '0.75rem', borderRadius: 'var(--radius-md)', color: '#60a5fa' }}>
            <Layers size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Total Chunks
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'var(--font-heading)' }}>
              {formatNumber(stats.total_chunks)}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: 'rgba(168, 85, 247, 0.15)', padding: '0.75rem', borderRadius: 'var(--radius-md)', color: '#c084fc' }}>
            <Type size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Avg Chunk Size
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'var(--font-heading)' }}>
              {formatNumber(stats.avg_chunk_size)} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>chars</span>
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.15)', padding: '0.75rem', borderRadius: 'var(--radius-md)', color: '#fbbf24' }}>
            <Clock size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Processing Time
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'var(--font-heading)' }}>
              {formatTime(processing_time_ms)}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '0.75rem', borderRadius: 'var(--radius-md)', color: '#34d399' }}>
            <FileCheck size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Total Chars
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'var(--font-heading)' }}>
              {formatNumber(stats.total_characters)}
            </div>
          </div>
        </div>
      </div>

      {/* Visualizations Chart */}
      <ChunkChart chunks={chunks} />

      {/* Individual Chunks List */}
      <div>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="var(--accent-purple)" />
          Individual Chunks ({chunks.length})
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {chunks.map((chunkText, index) => (
            <ChunkCard key={index} index={index} text={chunkText} totalChunks={chunks.length} />
          ))}
        </div>
      </div>
    </div>
  )
}
