import React from 'react'
import { CheckCircle, AlertCircle } from 'lucide-react'

interface HeaderProps {
  isConnected: boolean
  showStatus?: boolean
}

export const Header: React.FC<HeaderProps> = ({ isConnected, showStatus = true }) => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white text-blue-600 rounded-lg p-2 font-bold text-lg">TCG</div>
            <div>
              <h1 className="text-3xl font-bold">Test Case Generator</h1>
              <p className="text-blue-100 text-sm">AI-powered test case generation from Jira</p>
            </div>
          </div>
          {showStatus && (
            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-300" />
                  <span className="text-sm text-green-100">Connected</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-yellow-300" />
                  <span className="text-sm text-yellow-100">Not Connected</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
