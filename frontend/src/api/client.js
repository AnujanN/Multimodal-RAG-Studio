const API_BASE = '/api'

/**
 * Fetch all available chunking techniques grouped by category
 */
export async function getTechniques() {
  const res = await fetch(`${API_BASE}/techniques`)
  if (!res.ok) {
    throw new Error(`Failed to fetch techniques: ${res.statusText}`)
  }
  return res.json()
}

/**
 * Process text using selected chunking technique
 */
export async function processChunk({ technique, text, params = {}, sourceType = 'custom', sourceName = null }) {
  const res = await fetch(`${API_BASE}/chunk`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      technique,
      text,
      params,
      source_type: sourceType,
      source_name: sourceName,
    }),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Chunking failed: ${res.statusText}`)
  }

  return res.json()
}

/**
 * Fetch preset texts list
 */
export async function getPresets() {
  const res = await fetch(`${API_BASE}/presets`)
  if (!res.ok) {
    throw new Error(`Failed to fetch presets: ${res.statusText}`)
  }
  return res.json()
}

/**
 * Fetch single preset detail by name
 */
export async function getPresetDetail(name) {
  const res = await fetch(`${API_BASE}/presets/${name}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch preset detail: ${res.statusText}`)
  }
  return res.json()
}

/**
 * Upload document and extract text using Docling/RapidOCR backend
 */
export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Upload failed: ${res.statusText}`)
  }

  return res.json()
}

/**
 * Fetch history of chunking runs
 */
export async function getHistory(limit = 30) {
  const res = await fetch(`${API_BASE}/history?limit=${limit}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch history: ${res.statusText}`)
  }
  return res.json()
}

/**
 * Fetch single history detail
 */
export async function getHistoryDetail(id) {
  const res = await fetch(`${API_BASE}/history/${id}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch history item: ${res.statusText}`)
  }
  return res.json()
}

/**
 * Delete a history item
 */
export async function deleteHistoryItem(id) {
  const res = await fetch(`${API_BASE}/history/${id}`, {
    method: 'DELETE',
  })
  if (!res.ok) {
    throw new Error(`Failed to delete history item: ${res.statusText}`)
  }
  return true
}
