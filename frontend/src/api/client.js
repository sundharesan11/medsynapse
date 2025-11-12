import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for LLM processing
})

export const api = {
  // Health check
  async healthCheck() {
    const response = await apiClient.get('/')
    return response.data
  },

  // Process patient intake
  async processIntake(patientId, rawInput, sessionId = null) {
    const response = await apiClient.post('/intake', {
      patient_id: patientId,
      raw_input: rawInput,
      session_id: sessionId,
    })
    return response.data
  },

  // Get patient history
  async getPatientHistory(patientId) {
    const response = await apiClient.get(`/patient/${patientId}/history`)
    return response.data
  },

  // Search similar cases
  async searchCases(query, limit = 5, scoreThreshold = 0.5) {
    const response = await apiClient.post('/search', {
      query: query,
      limit: limit,
      score_threshold: scoreThreshold,
    })
    return response.data
  },

  // Get database statistics
  async getStats() {
    const response = await apiClient.get('/stats')
    return response.data
  },
}

export default apiClient
