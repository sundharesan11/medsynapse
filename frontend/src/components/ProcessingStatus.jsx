export default function ProcessingStatus() {
  return (
    <div className="card bg-blue-50 border-l-4 border-blue-500">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <svg
            className="animate-spin h-6 w-6 text-blue-600"
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
        </div>
        <div className="ml-4">
          <h3 className="text-blue-900 font-medium">Processing Patient Intake</h3>
          <p className="text-blue-700 text-sm mt-1">
            Multi-agent system is analyzing patient data...
          </p>
          <div className="mt-3 space-y-1 text-xs text-blue-600">
            <p>[1/5] Intake Agent: Extracting structured data</p>
            <p>[2/5] Summary Agent: Generating clinical summary</p>
            <p>[3/5] Knowledge Agent: Searching similar cases</p>
            <p>[4/5] Report Agent: Creating SOAP report</p>
            <p>[5/5] Storage Agent: Saving to database</p>
          </div>
        </div>
      </div>
    </div>
  )
}
