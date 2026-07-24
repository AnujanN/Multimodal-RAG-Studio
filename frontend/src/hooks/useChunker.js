import { useState, useEffect, useCallback } from 'react'
import { getTechniques, getPresets, getPresetDetail, processChunk, uploadFile, getHistory, deleteHistoryItem } from '../api/client'

export function useChunker() {
  // Data states
  const [techniques, setTechniques] = useState({ basic: [], advanced: [], ai_powered: [] })
  const [presets, setPresets] = useState([])
  const [history, setHistory] = useState([])
  
  // Selection states
  const [selectedTechnique, setSelectedTechnique] = useState('naive_chunker')
  const [parameters, setParameters] = useState({})
  
  // Input states
  const [sourceType, setSourceType] = useState('preset') // 'preset' | 'custom' | 'upload'
  const [selectedPreset, setSelectedPreset] = useState('technical_article')
  const [inputText, setInputText] = useState('')
  const [uploadInfo, setUploadInfo] = useState(null)
  
  // Results & UI states
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch initial metadata
  useEffect(() => {
    async function init() {
      try {
        const [techData, presetData, historyData] = await Promise.all([
          getTechniques(),
          getPresets(),
          getHistory().catch(() => []),
        ])
        if (techData.categories) {
          setTechniques(techData.categories)
        }
        setPresets(presetData || [])
        setHistory(historyData || [])

        // Load default preset text
        if (presetData && presetData.length > 0) {
          const detail = await getPresetDetail(presetData[0].name)
          setInputText(detail.text)
        }
      } catch (err) {
        console.error('Initialization error:', err)
        setError(err.message)
      }
    }
    init()
  }, [])

  // Find info of currently selected technique
  const getSelectedTechniqueInfo = useCallback(() => {
    for (const category of ['basic', 'advanced', 'ai_powered']) {
      const match = (techniques[category] || []).find(t => t.name === selectedTechnique)
      if (match) return match
    }
    return null
  }, [techniques, selectedTechnique])

  // Handle technique change & reset default parameters
  const handleTechniqueChange = (techName) => {
    setSelectedTechnique(techName)
    
    // Set default parameters for selected technique
    for (const category of ['basic', 'advanced', 'ai_powered']) {
      const tech = (techniques[category] || []).find(t => t.name === techName)
      if (tech && tech.parameters) {
        const defaults = {}
        tech.parameters.forEach(p => {
          defaults[p.name] = p.default
        })
        setParameters(defaults)
        break
      }
    }
  }

  // Handle preset change
  const handlePresetChange = async (presetName) => {
    setSelectedPreset(presetName)
    setSourceType('preset')
    try {
      const detail = await getPresetDetail(presetName)
      setInputText(detail.text)
      setUploadInfo(null)
    } catch (err) {
      setError(err.message)
    }
  }

  // Handle file upload
  const handleFileUpload = async (file) => {
    setUploading(true)
    setError(null)
    try {
      const res = await uploadFile(file)
      setInputText(res.text)
      setSourceType('upload')
      setUploadInfo({
        filename: res.filename,
        extension: res.extension,
        characterCount: res.character_count,
        parserUsed: res.parser_used,
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  // Execute chunking
  const handleProcessText = async () => {
    if (!inputText.trim()) {
      setError('Please provide input text before processing.')
      return
    }

    setLoading(true)
    setError(null)

    const sourceName = sourceType === 'preset' ? selectedPreset : (uploadInfo ? uploadInfo.filename : 'Custom Text')

    try {
      const res = await processChunk({
        technique: selectedTechnique,
        text: inputText,
        params: parameters,
        sourceType,
        sourceName,
      })
      setResult(res)
      
      // Refresh history list
      const updatedHistory = await getHistory().catch(() => [])
      setHistory(updatedHistory)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Handle history item selection
  const handleSelectHistoryItem = (item) => {
    setSelectedTechnique(item.technique)
    setParameters(item.parameters || {})
    setResult({
      id: item.id,
      technique: item.technique,
      chunks: item.chunks || [],
      stats: {
        total_chunks: item.total_chunks,
        total_characters: item.total_characters,
        avg_chunk_size: item.avg_chunk_size,
        min_chunk_size: item.min_chunk_size || 0,
        max_chunk_size: item.max_chunk_size || 0,
      },
      processing_time_ms: item.processing_time_ms,
      source_type: item.source_type,
      source_name: item.source_name,
    })
  }

  // Delete history item
  const handleDeleteHistory = async (id, e) => {
    if (e) e.stopPropagation()
    try {
      await deleteHistoryItem(id)
      setHistory(prev => prev.filter(h => h.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return {
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
    currentTechniqueInfo: getSelectedTechniqueInfo(),
    
    // Actions
    setParameters,
    setSourceType,
    setInputText,
    handleTechniqueChange,
    handlePresetChange,
    handleFileUpload,
    handleProcessText,
    handleSelectHistoryItem,
    handleDeleteHistory,
    clearError: () => setError(null),
  }
}
