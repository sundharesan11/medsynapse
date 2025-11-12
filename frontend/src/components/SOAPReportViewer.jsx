export default function SOAPReportViewer({ report, patientId }) {
  if (!report) return null

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">SOAP Report Generated</h3>
            <p className="text-sm text-gray-600 mt-1">
              Patient ID: <span className="font-medium">{patientId}</span>
            </p>
            <p className="text-sm text-gray-600">
              Generated: {formatDate(report.generated_at)}
            </p>
          </div>
          {report.confidence_level && (
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                report.confidence_level === 'high'
                  ? 'bg-green-100 text-green-800'
                  : report.confidence_level === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              Confidence: {report.confidence_level}
            </span>
          )}
        </div>
      </div>

      {/* Clinical Flags */}
      {report.flags && report.flags.length > 0 && (
        <div className="card bg-amber-50 border-l-4 border-amber-400">
          <h4 className="font-semibold text-amber-900 mb-2">Clinical Flags</h4>
          <ul className="space-y-1">
            {report.flags.map((flag, index) => (
              <li key={index} className="text-amber-800 text-sm flex items-start">
                <span className="mr-2">[!]</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* SOAP Sections */}
      <div className="space-y-4">
        {/* Subjective */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            S - Subjective
          </h4>
          <p className="text-gray-700 whitespace-pre-wrap">{report.subjective}</p>
        </div>

        {/* Objective */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            O - Objective
          </h4>
          <p className="text-gray-700 whitespace-pre-wrap">{report.objective}</p>
        </div>

        {/* Assessment */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            A - Assessment
          </h4>
          <p className="text-gray-700 whitespace-pre-wrap">{report.assessment}</p>
        </div>

        {/* Plan */}
        <div className="card">
          <h4 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            P - Plan
          </h4>
          <p className="text-gray-700 whitespace-pre-wrap">{report.plan}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="card bg-gray-50">
        <div className="flex gap-3">
          <button
            onClick={() => window.print()}
            className="btn-secondary text-sm"
          >
            Print Report
          </button>
          <button
            onClick={() => {
              const reportText = `
SOAP REPORT
Patient ID: ${patientId}
Generated: ${formatDate(report.generated_at)}
Confidence: ${report.confidence_level || 'N/A'}

SUBJECTIVE:
${report.subjective}

OBJECTIVE:
${report.objective}

ASSESSMENT:
${report.assessment}

PLAN:
${report.plan}

${report.flags && report.flags.length > 0 ? `\nCLINICAL FLAGS:\n${report.flags.map(f => `- ${f}`).join('\n')}` : ''}
              `.trim()

              navigator.clipboard.writeText(reportText)
              alert('Report copied to clipboard!')
            }}
            className="btn-secondary text-sm"
          >
            Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  )
}
