import React, { useState } from 'react'
import { Loader, CheckCircle, AlertCircle, Eye, EyeOff } from 'lucide-react'
import { jiraAPI, JiraCredentials } from '../api'

interface ConnectionPanelProps {
  onConnect: (credentials: JiraCredentials) => void
  onConnectionStatusChange: (isConnected: boolean) => void
}

export const ConnectionPanel: React.FC<ConnectionPanelProps> = ({
  onConnect,
  onConnectionStatusChange,
}) => {
  const [credentials, setCredentials] = useState<JiraCredentials>({
    jira_url: '',
    email: '',
    api_token: '',
  })

  const [testing, setTesting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [error, setError] = useState('')
  const [showToken, setShowToken] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }))
    setConnectionStatus('idle')
    setError('')
  }

  const handleTestConnection = async () => {
    if (!credentials.jira_url || !credentials.email || !credentials.api_token) {
      setError('All fields are required')
      return
    }

    setTesting(true)
    setError('')

    try {
      await jiraAPI.testConnection(credentials)
      setConnectionStatus('success')
      onConnectionStatusChange(true)
      onConnect(credentials)
    } catch (err: any) {
      setConnectionStatus('error')
      setError(err.response?.data?.detail || 'Connection failed. Check your credentials.')
      onConnectionStatusChange(false)
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span className="text-blue-600">⚙️</span> Jira Connection
      </h2>

      <div className="space-y-4">
        {/* Jira URL */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Jira Base URL <span className="text-red-500">*</span>
          </label>
          <input
            type="url"
            name="jira_url"
            placeholder="https://your-company.atlassian.net"
            value={credentials.jira_url}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">e.g., https://company.atlassian.net</p>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            name="email"
            placeholder="your-email@company.com"
            value={credentials.email}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* API Token */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            API Token <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type={showToken ? 'text' : 'password'}
              name="api_token"
              placeholder="enter your API token"
              value={credentials.api_token}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setShowToken(!showToken)}
              className="absolute right-3 top-2.5 text-gray-500 hover:text-gray-700"
            >
              {showToken ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Token is never stored. Get it from Jira Settings → Security
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Success Message */}
        {connectionStatus === 'success' && (
          <div className="flex gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
            <CheckCircle size={20} className="flex-shrink-0 mt-0.5" />
            <span className="text-sm">Successfully connected to Jira!</span>
          </div>
        )}

        {/* Test Connection Button */}
        <button
          onClick={handleTestConnection}
          disabled={testing || !credentials.jira_url || !credentials.email || !credentials.api_token}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
        >
          {testing ? (
            <>
              <Loader size={18} className="animate-spin" />
              Testing Connection...
            </>
          ) : (
            'Test Connection'
          )}
        </button>
      </div>
    </div>
  )
}
