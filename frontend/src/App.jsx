import React from 'react'
import { Header } from './components/Header'
import { TechniqueSelector } from './components/TechniqueSelector'
import { ParameterControls } from './components/ParameterControls'
import { InputPanel } from './components/InputPanel'
import { ResultsDashboard } from './components/ResultsDashboard'
import { HistoryPanel } from './components/HistoryPanel'
import { useChunker } from './hooks/useChunker'
import { AlertTriangle, X } from 'lucide-react'

export default function App() {
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
            justify: 'space-between',
            fontSize: '0.9rem',
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

      {/* Main Grid Layout */}
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
    </div>
  )
}
