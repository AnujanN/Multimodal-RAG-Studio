import React, { useState } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import { LandingPage } from './pages/LandingPage'
import { AuthPage } from './pages/AuthPage'
import { CredentialSetupModal } from './components/CredentialSetupModal'
import { Header } from './components/Header'
import { TechniqueSelector } from './components/TechniqueSelector'
import { ParameterControls } from './components/ParameterControls'
import { InputPanel } from './components/InputPanel'
import { ResultsDashboard } from './components/ResultsDashboard'
import { HistoryPanel } from './components/HistoryPanel'
import { RagChatPanel } from './components/RagChatPanel'
import { useChunker } from './hooks/useChunker'
import { AlertTriangle, X, Scissors, Sparkles } from 'lucide-react'

// ── Authenticated App Shell ───────────────────────────────────────────────────
function AuthedApp() {
  const { user, credStatus } = useAuth()
  const [activeTab, setActiveTab] = useState('rag')
  const [showCredModal, setShowCredModal] = useState(false)
  const [showSetupModal, setShowSetupModal] = useState(false)

  // Show credential setup modal after signup if not configured and not admin
  const needsSetup = user && credStatus !== null && !credStatus?.configured && !credStatus?.is_admin
  const [setupDismissed, setSetupDismissed] = useState(false)

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
      {/* Header with user info + settings button */}
      <Header onOpenSettings={() => setShowCredModal(true)} />

      {/* Tab Navigation */}
      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.75rem',
        }}
      >
        <button
          onClick={() => setActiveTab('rag')}
          className={`nav-tab ${activeTab === 'rag' ? 'active' : ''}`}
        >
          <Sparkles size={17} />
          <span>Multimodal RAG Studio</span>
        </button>

        <button
          onClick={() => setActiveTab('playground')}
          className={`nav-tab ${activeTab === 'playground' ? 'active' : ''}`}
        >
          <Scissors size={17} />
          <span>21 Chunking Strategies Lab</span>
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#fca5a5',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.88rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={16} color="#ef4444" />
            <span>{error}</span>
          </div>
          <button onClick={clearError} style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer' }}>
            <X size={15} />
          </button>
        </div>
      )}

      {/* RAG Tab */}
      {activeTab === 'rag' && <RagChatPanel credStatus={credStatus} onOpenSettings={() => setShowCredModal(true)} />}

      {/* Chunking Lab Tab */}
      {activeTab === 'playground' && (
        <div className="main-layout">
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
            <ResultsDashboard result={result} />
            <HistoryPanel
              history={history}
              onSelectHistoryItem={handleSelectHistoryItem}
              onDeleteHistory={handleDeleteHistory}
            />
          </div>
        </div>
      )}

      {/* Credential Setup Modal — shown after signup if not configured */}
      {needsSetup && !setupDismissed && (
        <CredentialSetupModal
          onDone={() => setSetupDismissed(true)}
          onSkip={() => setSetupDismissed(true)}
        />
      )}

      {/* Settings Modal — triggered by header button */}
      {showCredModal && (
        <CredentialSetupModal
          isSettings
          onDone={() => setShowCredModal(false)}
          onSkip={() => setShowCredModal(false)}
        />
      )}
    </div>
  )
}

// ── Root App with Auth Gate ───────────────────────────────────────────────────
function AppRouter() {
  const { user } = useAuth()
  const [page, setPage] = useState('landing') // 'landing' | 'login' | 'signup'

  // If logged in, show the app shell
  if (user) return <AuthedApp />

  // Landing Page
  if (page === 'landing') {
    return (
      <LandingPage
        onLoginClick={() => setPage('login')}
        onSignupClick={() => setPage('signup')}
      />
    )
  }

  // Auth Page (login or signup)
  return (
    <AuthPage
      initialTab={page}
      onBack={() => setPage('landing')}
    />
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  )
}
