import React, { useState } from 'react'
import { Header } from './components/Header'
import { ConnectionPanel } from './components/ConnectionPanel'
import { InputPanel } from './components/InputPanel'
import { ContextCard } from './components/ContextCard'
import { TestCasesTable } from './components/TestCasesTable'
import { JiraCredentials } from './api'
import { IssueData, TestCase } from './types'

export default function App() {
  const [credentials, setCredentials] = useState<JiraCredentials | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [selectedIssue, setSelectedIssue] = useState<IssueData | null>(null)
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleConnect = (creds: JiraCredentials) => {
    setCredentials(creds)
  }

  const handleConnectionStatusChange = (connected: boolean) => {
    setIsConnected(connected)
  }

  const handleIssueLoaded = (issue: IssueData) => {
    setSelectedIssue(issue)
  }

  const handleTestCasesGenerated = (cases: TestCase[]) => {
    setTestCases(cases)
  }

  const handleError = (errorMsg: string) => {
    setError(errorMsg)
    setTimeout(() => setError(null), 5000)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header isConnected={isConnected} />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
            <p className="text-red-700 font-semibold flex items-center gap-2">
              <span className="text-lg">❌</span> {error}
            </p>
          </div>
        )}

        {isLoading && (
          <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
            <p className="text-blue-700 font-semibold flex items-center gap-2">
              <span className="inline-block animate-spin text-lg">⏳</span> Processing your
              request...
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel */}
          <div className="lg:col-span-1 space-y-6">
            <ConnectionPanel
              onConnect={handleConnect}
              onConnectionStatusChange={handleConnectionStatusChange}
            />

            <InputPanel
              credentials={credentials}
              onIssueLoaded={handleIssueLoaded}
              onTestCasesGenerated={handleTestCasesGenerated}
              onLoading={setIsLoading}
              onError={handleError}
            />
          </div>

          {/* Right Panel */}
          <div className="lg:col-span-2 space-y-6">
            <ContextCard issue={selectedIssue} />

            <TestCasesTable 
              testCases={testCases}
              onTestCasesChange={setTestCases}
            />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 py-6 text-center text-gray-600 text-sm border-t border-gray-300">
          <p>Test Case Generator v1.0.0 • Powered by Groq (Mixtral) • Jira Integration</p>
        </footer>
      </main>
    </div>
  )
}
