import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function PatientHistory() {
  const [patientId, setPatientId] = useState('')
  const [history, setHistory] = useState(null)
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchHistory = async (e) => {
    e.preventDefault()

    if (!patientId.trim()) {
      setError('Please enter a patient ID')
      return
    }

    setLoading(true)
    setError('')
    setHistory(null)
    setSummary('')

    try {
      const response = await axios.get(`${API_URL}/history/${patientId}?limit=10`)

      if (response.data.success) {
        setHistory(response.data.history)
        setSummary(response.data.summary)
      } else {
        setError('Failed to fetch patient history')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching patient history')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoDate) => {
    try {
      const date = new Date(isoDate)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return isoDate
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Patient Medical History
        </h1>
        <p className="text-gray-600">
          View a patient's historical visits and SOAP reports
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <form onSubmit={fetchHistory} className="flex gap-4">
          <div className="flex-1">
            <label htmlFor="patientId" className="block text-sm font-medium text-gray-700 mb-2">
              Patient ID
            </label>
            <input
              type="text"
              id="patientId"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="e.g., P12345"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Loading...' : 'View History'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">
            History Summary
          </h2>
          <pre className="text-sm text-blue-800 whitespace-pre-wrap font-sans">
            {summary}
          </pre>
        </div>
      )}

      {/* History Results */}
      {history && history.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            No historical visits found for patient <strong>{patientId}</strong>.
            This appears to be their first visit.
          </p>
        </div>
      )}

      {history && history.length > 0 && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Previous Visits ({history.length})
          </h2>

          {history.map((visit, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              {/* Visit Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Visit {index + 1}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {formatDate(visit.timestamp)}
                  </p>
                </div>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                  Historical
                </span>
              </div>

              {/* Chief Complaint */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-1">
                  Chief Complaint
                </h4>
                <p className="text-gray-900">
                  {visit.chief_complaint || 'N/A'}
                </p>
              </div>

              {/* Symptoms */}
              {visit.symptoms && visit.symptoms.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Symptoms
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {visit.symptoms.map((symptom, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                      >
                        {symptom}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Assessment */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-1">
                  Assessment
                </h4>
                <p className="text-gray-900 whitespace-pre-wrap">
                  {visit.assessment || 'N/A'}
                </p>
              </div>

              {/* Medical History */}
              {visit.medical_history && visit.medical_history.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Medical History
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {visit.medical_history.map((condition, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm"
                      >
                        {condition}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
