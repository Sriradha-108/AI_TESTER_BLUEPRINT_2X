import React from 'react'
import { IssueData } from '../types'

interface ContextCardProps {
  issue: IssueData | null
}

export const ContextCard: React.FC<ContextCardProps> = ({ issue }) => {
  if (!issue) {
    return (
      <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-6 text-center text-gray-500">
        <p className="text-sm">Load a Jira issue to see its details</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span className="text-purple-600">📋</span> Issue Context
      </h2>

      <div className="space-y-4">
        {/* Header info */}
        <div className="flex items-center justify-between pb-4 border-b">
          <div>
            <span className="font-mono text-lg font-bold text-blue-600">{issue.key}</span>
            <span className="text-sm text-gray-500 ml-2">•</span>
            <span className="text-sm text-gray-600 ml-2">{issue.issue_type}</span>
          </div>
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded">
            {issue.priority}
          </span>
        </div>

        {/* Summary */}
        <div>
          <h3 className="font-semibold text-gray-700 text-sm mb-1">Summary</h3>
          <p className="text-gray-800 line-clamp-2">{issue.summary}</p>
        </div>

        {/* Description */}
        <div>
          <h3 className="font-semibold text-gray-700 text-sm mb-1">Description</h3>
          <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 max-h-40 overflow-y-auto line-clamp-4">
            {issue.description || <em className="text-gray-500">No description provided</em>}
          </div>
        </div>

        {/* Acceptance Criteria */}
        <div>
          <h3 className="font-semibold text-gray-700 text-sm mb-1">Acceptance Criteria</h3>
          <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 max-h-40 overflow-y-auto">
            {issue.acceptance_criteria ? (
              <pre className="whitespace-pre-wrap font-sans">{issue.acceptance_criteria}</pre>
            ) : (
              <em className="text-gray-500">No acceptance criteria provided</em>
            )}
          </div>
        </div>

        {/* Components */}
        {issue.linked_components && issue.linked_components.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-700 text-sm mb-2">Components</h3>
            <div className="flex flex-wrap gap-2">
              {issue.linked_components.map(component => (
                <span
                  key={component}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                >
                  {component}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4 text-xs text-gray-600 pt-2 border-t">
          <div>
            <span className="font-semibold">Created:</span>
            <br />
            {new Date(issue.created_at).toLocaleDateString()}
          </div>
          <div>
            <span className="font-semibold">Updated:</span>
            <br />
            {new Date(issue.updated_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  )
}
