import React, { useState } from 'react'
import { Header } from './components/Header'
import { TechniqueSelector } from './components/TechniqueSelector'
import { ParameterControls } from './components/ParameterControls'
import { InputPanel } from './components/InputPanel'
import { ResultsDashboard } from './components/ResultsDashboard'
import { HistoryPanel } from './components/HistoryPanel'
import { RagChatPanel } from './components/RagChatPanel'
import { useChunker } from './hooks/useChunker'
import { AlertTriangle, X, Scissors, Sparkles } from 'lucide-react'

export default function App() {
  const [activeTab, setActiveTab] = useState('rag') // 'playground' | 'rag'

  const {
    techniques,
    presets,
    history,
    selectedTechnique,
    parameters,
    sourceType,
    selectedPreset,
    inputText,
    uploadInfo,
    result,
    loading,
    uploading,
    error,
    currentTechniqueInfo,
    setParameters,
    setSourceType,
    setInputText,
    handleTechniqueChange,
    handlePresetChange,
    handleFileUpload,
    handleProcessText,
    handleSelectHistoryItem,
    handleDeleteHistory,
    clearError,
  } = useChunker()

  return (
    <div className="app-container">
      {/* Header */}
      <Header />

      {/* Mode Navigation Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          marginBottom: '1rem',
          borderBottom: '1px solid var(--border-color, #313244)',
          paddingBottom: '0.75rem',
        }}
      >
        <button
          onClick={() => setActiveTab('rag')}
          style={{
            background: activeTab === 'rag' ? 'rgba(137, 180, 250, 0.15)' : 'transparent',
            border: `1px solid ${activeTab === 'rag' ? '#89b4fa' : 'transparent'}`,
            color: activeTab === 'rag' ? '#89b4fa' : '#a6adc8',
            padding: '0.6rem 1.2rem',
            borderRadius: 'var(--radius-md, 8px)',
            fontWeight: 600,
            fontSize: '0.92rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
        >
          <Sparkles size={18} />
          <span>Multimodal RAG Studio</span>
        </button>

        <button
          onClick={() => setActiveTab('playground')}
          style={{
            background: activeTab === 'playground' ? 'rgba(203, 166, 247, 0.15)' : 'transparent',
            border: `1px solid ${activeTab === 'playground' ? '#cba6f7' : 'transparent'}`,
            color: activeTab === 'playground' ? '#cba6f7' : '#a6adc8',
            padding: '0.6rem 1.2rem',
            borderRadius: 'var(--radius-md, 8px)',
            fontWeight: 600,
            fontSize: '0.92rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
        >
          <Scissors size={18} />
          <span>21 Chunking Strategies Lab</span>
        </button>
      </div>

      {/* Error Alert Banner */}
      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fca5a5',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.9rem',
            marginBottom: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={18} color="#ef4444" />
            <span>{error}</span>
          </div>
          <button
            onClick={clearError}
            style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* RAG Mode */}
      {activeTab === 'rag' && <RagChatPanel />}

      {/* Chunking Strategies Playground Mode */}
      {activeTab === 'playground' && (
        <div className="main-layout">
          {/* Left Sidebar: Controls */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <TechniqueSelector
              techniques={techniques}
              selectedTechnique={selectedTechnique}
              onTechniqueChange={handleTechniqueChange}
              currentInfo={currentTechniqueInfo}
            />

            <ParameterControls
              currentInfo={currentTechniqueInfo}
              parameters={parameters}
              onParameterChange={setParameters}
            />
          </div>

          {/* Right Area: Input & Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <InputPanel
              sourceType={sourceType}
              setSourceType={setSourceType}
              presets={presets}
              selectedPreset={selectedPreset}
              onPresetChange={handlePresetChange}
              inputText={inputText}
              setInputText={setInputText}
              uploadInfo={uploadInfo}
              onFileUpload={handleFileUpload}
              uploading={uploading}
              loading={loading}
              onProcessText={handleProcessText}
            />

            {/* Results Dashboard */}
            <ResultsDashboard result={result} />

            {/* History Panel */}
            <HistoryPanel
              history={history}
              onSelectHistoryItem={handleSelectHistoryItem}
              onDeleteHistory={handleDeleteHistory}
            />
          </div>
        </div>
      )}
    </div>
  )
}
