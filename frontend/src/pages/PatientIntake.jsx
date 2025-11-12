import { useState } from 'react'
import { api } from '../api/client'
import SOAPReportViewer from '../components/SOAPReportViewer'
import ProcessingStatus from '../components/ProcessingStatus'

export default function PatientIntake() {
  const [patientId, setPatientId] = useState('')
  const [rawInput, setRawInput] = useState('')
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setProcessing(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.processIntake(patientId, rawInput)

      if (response.success) {
        setResult(response)
      } else {
        setError(response.message || 'Processing failed')
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to process intake')
    } finally {
      setProcessing(false)
    }
  }

  const handleReset = () => {
    setPatientId('')
    setRawInput('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Patient Intake</h2>
        <p className="mt-1 text-sm text-gray-600">
          Enter patient information to generate a SOAP report using multi-agent AI system
        </p>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="patientId" className="block text-sm font-medium text-gray-700 mb-2">
              Patient ID
            </label>
            <input
              type="text"
              id="patientId"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="input-field"
              placeholder="e.g., P12345"
              required
              disabled={processing}
            />
          </div>

          <div>
            <label htmlFor="rawInput" className="block text-sm font-medium text-gray-700 mb-2">
              Patient Information
            </label>
            <textarea
              id="rawInput"
              value={rawInput}
              onChange={(e) => setRawInput(e.target.value)}
              className="input-field"
              rows={10}
              placeholder="Enter patient information including:
- Chief complaint
- Symptoms and duration
- Medical history
- Current medications
- Vital signs
- Allergies

Example:
58-year-old male presents with chest tightness and sweating.
Pain started 2 hours ago, described as pressure-like sensation.
History of hypertension and diabetes.
Taking Metformin 1000mg and Lisinopril 10mg.
Blood pressure: 160/95, Heart rate: 98"
              required
              disabled={processing}
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={processing}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? 'Processing...' : 'Process Patient Intake'}
            </button>

            {(result || error) && (
              <button
                type="button"
                onClick={handleReset}
                className="btn-secondary"
                disabled={processing}
              >
                Reset
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Processing Status */}
      {processing && <ProcessingStatus />}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error</h3>
          <p className="text-red-700 text-sm mt-1">{error}</p>
        </div>
      )}

      {/* SOAP Report Result */}
      {result && result.success && (
        <SOAPReportViewer
          report={result.soap_report}
          patientId={result.patient_id}
        />
      )}
    </div>
  )
}
