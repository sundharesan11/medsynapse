import { useState } from 'react'
import { api } from '../api/client'

export default function SearchCases() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setSearched(true)
    setError(null)

    try {
      const response = await api.searchCases(query, 10, 0.5)

      if (response.success) {
        setResults(response.results || [])
      } else {
        setError(response.message || 'Search failed')
        setResults([])
      }
    } catch (error) {
      console.error('Search failed:', error)
      setError(error.message || 'Failed to search cases')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Search Similar Cases</h2>
        <p className="mt-1 text-sm text-gray-600">
          Search for similar patient cases using semantic search
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <input
              type="text"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input-field"
              placeholder="e.g., chest pain and breathing difficulty"
              required
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter symptoms or conditions to find similar cases
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search Cases'}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="card bg-red-50 border-l-4 border-red-500">
          <h4 className="font-medium text-red-900 mb-2">Error</h4>
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {loading && (
        <div className="card bg-blue-50">
          <div className="flex items-center">
            <svg
              className="animate-spin h-5 w-5 text-blue-600 mr-3"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span className="text-blue-900">Searching vector database...</span>
          </div>
        </div>
      )}

      {searched && !loading && results.length === 0 && (
        <div className="card bg-gray-50 text-center py-8">
          <p className="text-gray-600">No similar cases found</p>
          <p className="text-sm text-gray-500 mt-1">
            Try a different search query or add more cases to the database
          </p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Found {results.length} similar cases
          </h3>
          {results.map((result, index) => (
            <div key={index} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-900">
                      Patient {result.patient_id}
                    </span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        result.score >= 0.75
                          ? 'bg-green-100 text-green-800'
                          : result.score >= 0.6
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {Math.round(result.score * 100)}% match
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    <span className="font-medium">Chief Complaint:</span> {result.chief_complaint}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">Symptoms:</span> {result.symptoms.join(', ')}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="card bg-blue-50 border-l-4 border-blue-500">
        <h4 className="font-medium text-blue-900 mb-2">How Semantic Search Works</h4>
        <p className="text-sm text-blue-800">
          The system uses embeddings to understand the meaning of symptoms, not just keywords.
          For example, searching for "chest pain" will also find cases with "cardiac discomfort"
          or "thoracic pain" because they have similar clinical meaning.
        </p>
      </div>
    </div>
  )
}
