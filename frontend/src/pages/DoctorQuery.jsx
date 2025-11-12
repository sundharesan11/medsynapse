import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function DoctorQuery() {
  const [patientId, setPatientId] = useState('')
  const [question, setQuestion] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async (e) => {
    e.preventDefault()

    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    // Add user question to chat
    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toISOString()
    }

    setChatHistory(prev => [...prev, userMessage])
    setLoading(true)
    setError('')

    const currentQuestion = question
    setQuestion('') // Clear input

    try {
      const response = await axios.post(`${API_URL}/query`, {
        patient_id: patientId.trim() || null,
        question: currentQuestion,
        limit: 5
      })

      // Add AI response to chat
      const aiMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources || [],
        num_sources: response.data.num_sources || 0,
        timestamp: new Date().toISOString()
      }

      setChatHistory(prev => [...prev, aiMessage])
    } catch (err) {
      setError(err.response?.data?.detail || 'Error processing query')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setChatHistory([])
    setError('')
  }

  const formatDate = (isoDate) => {
    try {
      const date = new Date(isoDate)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return isoDate
    }
  }

  const exampleQuestions = [
    "What medications has the patient been prescribed?",
    "Summarize the patient's previous diagnoses",
    "Has the patient had any previous visits for chest pain?",
    "What were the assessments from the last 3 visits?",
    "Are there any patterns in the patient's symptoms?"
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Doctor Query Assistant
        </h1>
        <p className="text-gray-600">
          Ask natural-language questions about patient history using AI-powered retrieval
        </p>
      </div>

      {/* Patient ID (Optional) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
        <label htmlFor="patientId" className="block text-sm font-medium text-gray-700 mb-2">
          Patient ID (Optional - leave blank to search all patients)
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

      {/* Chat Container */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Chat History */}
        <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
          {chatHistory.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <p className="text-gray-600 mb-4">No questions asked yet</p>
              <div className="text-left max-w-md mx-auto">
                <p className="text-sm font-medium text-gray-700 mb-2">Try asking:</p>
                <ul className="space-y-2">
                  {exampleQuestions.slice(0, 3).map((q, idx) => (
                    <li key={idx} className="text-sm text-gray-600">
                      • {q}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {chatHistory.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}
              >
                <div className="flex items-start gap-3">
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}

                  <div className="flex-1">
                    <p className="whitespace-pre-wrap">{message.content}</p>

                    {/* Sources for AI responses */}
                    {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-medium text-gray-500 mb-2">
                          Sources ({message.num_sources} record{message.num_sources !== 1 ? 's' : ''} retrieved):
                        </p>
                        <div className="space-y-2">
                          {message.sources.map((source, idx) => (
                            <div key={idx} className="text-xs text-gray-600 bg-gray-50 rounded p-2">
                              <span className="font-medium">Visit {idx + 1}</span>
                              {source.timestamp && (
                                <span className="text-gray-500"> • {formatDate(source.timestamp)}</span>
                              )}
                              {source.chief_complaint && (
                                <div className="mt-1">{source.chief_complaint}</div>
                              )}
                              {source.score && (
                                <div className="text-gray-400 mt-1">
                                  Similarity: {(source.score * 100).toFixed(1)}%
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-4 max-w-3xl">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <span className="text-sm text-gray-500 ml-2">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-white">
          {error && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={askQuestion} className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about patient history..."
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Sending...' : 'Ask'}
            </button>
            {chatHistory.length > 0 && (
              <button
                type="button"
                onClick={clearChat}
                className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Clear
              </button>
            )}
          </form>
        </div>
      </div>

      {/* Example Questions */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-3">
          Example Questions:
        </h3>
        <div className="flex flex-wrap gap-2">
          {exampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(q)}
              className="px-3 py-1 bg-white border border-blue-200 text-blue-700 rounded-full text-sm hover:bg-blue-100 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-gray-100 border border-gray-300 rounded-lg p-4">
        <div className="flex gap-3">
          <svg className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-gray-700">
            <p className="font-medium mb-1">How it works:</p>
            <ul className="space-y-1 text-gray-600">
              <li>• Searches patient history using semantic search</li>
              <li>• Uses Groq LLM to generate answers based on retrieved data</li>
              <li>• All queries are traced in LangSmith for debugging</li>
              <li>• Provides source citations for transparency</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
