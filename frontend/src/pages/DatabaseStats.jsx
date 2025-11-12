import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function DatabaseStats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.getStats()

      if (response.success) {
        setStats({
          totalCases: response.stats.total_cases || 0,
          vectorDimension: response.stats.vector_dimension || 384,
          status: response.stats.status || 'unknown',
        })
      } else {
        setError(response.message || 'Failed to fetch stats')
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Database Statistics</h2>
        <div className="card">
          <p className="text-gray-600">Loading statistics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Database Statistics</h2>
        <div className="card bg-red-50">
          <p className="text-red-800">Error loading statistics: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Database Statistics</h2>
          <p className="mt-1 text-sm text-gray-600">
            Overview of the patient case database
          </p>
        </div>
        <button
          onClick={fetchStats}
          className="btn-secondary text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Cases</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalCases || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Vector Dimension</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.vectorDimension || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                stats?.status === 'ready' ? 'bg-green-100' : 'bg-gray-100'
              }`}>
                <svg
                  className={`w-6 h-6 ${stats?.status === 'ready' ? 'text-green-600' : 'text-gray-600'}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Database Status</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">{stats?.status || 'Unknown'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Embedding Model</dt>
            <dd className="mt-1 text-sm text-gray-900">all-MiniLM-L6-v2</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Vector Database</dt>
            <dd className="mt-1 text-sm text-gray-900">Qdrant</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">LLM Provider</dt>
            <dd className="mt-1 text-sm text-gray-900">Groq (Llama 3.3 70B)</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Orchestration</dt>
            <dd className="mt-1 text-sm text-gray-900">LangGraph Multi-Agent</dd>
          </div>
        </dl>
      </div>

      {/* Database Health */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Database Health</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Vector Storage</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
              Operational
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Embedding Service</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
              Operational
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Search Index</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
              Operational
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
