import React, { useState } from 'react'
import { Copy, Download, Edit2, Save, X } from 'lucide-react'
import { TestCase } from '../types'
import { testCasesAPI } from '../api'

interface TestCasesTableProps {
  testCases: TestCase[]
  onTestCasesChange?: (cases: TestCase[]) => void
}

export const TestCasesTable: React.FC<TestCasesTableProps> = ({
  testCases,
  onTestCasesChange,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editedCase, setEditedCase] = useState<TestCase | null>(null)
  const [exporting, setExporting] = useState<'csv' | 'tsv' | 'markdown' | null>(null)

  const handleEditStart = (testCase: TestCase) => {
    setEditingId(testCase.id)
    setEditedCase({ ...testCase })
  }

  const handleEditSave = () => {
    if (editedCase && onTestCasesChange) {
      const updated = testCases.map(tc => (tc.id === editedCase.id ? editedCase : tc))
      onTestCasesChange(updated)
    }
    setEditingId(null)
    setEditedCase(null)
  }

  const handleEditCancel = () => {
    setEditingId(null)
    setEditedCase(null)
  }

  const handleCopyToClipboard = async () => {
    try {
      const tsv = testCases
        .map(tc => [
          tc.id,
          tc.title,
          tc.type,
          tc.priority,
          tc.preconditions,
          tc.steps.join('\n'),
          tc.test_data,
          tc.expected_result,
          tc.linked_jira_id,
        ])
        .map(row => row.join('\t'))
        .join('\n')

      const header = [
        'ID',
        'Title',
        'Type',
        'Priority',
        'Preconditions',
        'Steps',
        'Test Data',
        'Expected Result',
        'Linked Jira ID',
      ].join('\t')

      await navigator.clipboard.writeText(header + '\n' + tsv)
      alert('Test cases copied to clipboard (TSV format)!')
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleExport = async (format: 'csv' | 'tsv' | 'markdown') => {
    setExporting(format)
    try {
      const blob = await testCasesAPI.export(testCases, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      const extension = format === 'markdown' ? 'md' : format
      a.download = `test_cases_${new Date().toISOString().split('T')[0]}.${extension}`

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed:', err)
      alert('Failed to export test cases')
    } finally {
      setExporting(null)
    }
  }

  if (testCases.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center text-gray-500">
        <p className="text-sm">Generate test cases to see them here</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-gray-100 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span className="text-emerald-600">✅</span> Generated Test Cases ({testCases.length})
        </h2>

        <div className="flex gap-2">
          <button
            onClick={handleCopyToClipboard}
            className="flex items-center gap-2 px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition text-sm font-semibold"
            title="Copy as TSV for Jira/Xray"
          >
            <Copy size={16} />
            Copy TSV
          </button>

          <button
            onClick={() => handleExport('csv')}
            disabled={exporting === 'csv'}
            className="flex items-center gap-2 px-3 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50 transition text-sm font-semibold"
          >
            <Download size={16} />
            CSV
          </button>

          <button
            onClick={() => handleExport('markdown')}
            disabled={exporting === 'markdown'}
            className="flex items-center gap-2 px-3 py-2 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50 transition text-sm font-semibold"
          >
            <Download size={16} />
            MD
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">ID</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Title</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Type</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Priority</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Preconditions</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700">Expected Result</th>
              <th className="px-4 py-3 text-center font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {testCases.map((tc, index) => (
              <tr
                key={tc.id}
                className="border-b border-gray-200 hover:bg-gray-50 transition"
              >
                {editingId === tc.id && editedCase ? (
                  // Edit mode
                  <>
                    <td className="px-4 py-3 font-mono text-sm text-blue-600">{tc.id}</td>
                    <td className="px-4 py-3">
                      <input
                        type="text"
                        value={editedCase.title}
                        onChange={e =>
                          setEditedCase({ ...editedCase, title: e.target.value })
                        }
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={editedCase.type}
                        onChange={e =>
                          setEditedCase({
                            ...editedCase,
                            type: e.target.value as TestCase['type'],
                          })
                        }
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                      >
                        <option>Positive</option>
                        <option>Negative</option>
                        <option>Edge</option>
                        <option>Boundary</option>
                        <option>Security</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={editedCase.priority}
                        onChange={e =>
                          setEditedCase({
                            ...editedCase,
                            priority: e.target.value as 'P0' | 'P1' | 'P2',
                          })
                        }
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                      >
                        <option>P0</option>
                        <option>P1</option>
                        <option>P2</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <textarea
                        value={editedCase.preconditions}
                        onChange={e =>
                          setEditedCase({
                            ...editedCase,
                            preconditions: e.target.value,
                          })
                        }
                        className="w-full px-2 py-1 border border-gray-300 rounded text-xs h-16"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <textarea
                        value={editedCase.expected_result}
                        onChange={e =>
                          setEditedCase({
                            ...editedCase,
                            expected_result: e.target.value,
                          })
                        }
                        className="w-full px-2 py-1 border border-gray-300 rounded text-xs h-16"
                      />
                    </td>
                    <td className="px-4 py-3 text-center space-x-2">
                      <button
                        onClick={handleEditSave}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-xs"
                        title="Save changes"
                      >
                        <Save size={14} /> Save
                      </button>
                      <button
                        onClick={handleEditCancel}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs"
                        title="Discard changes"
                      >
                        <X size={14} />
                      </button>
                    </td>
                  </>
                ) : (
                  // View mode
                  <>
                    <td className="px-4 py-3 font-mono text-sm font-bold text-blue-600">
                      {tc.id}
                    </td>
                    <td className="px-4 py-3 font-semibold text-gray-900 max-w-xs truncate">
                      {tc.title}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-700">
                        {tc.type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          tc.priority === 'P0'
                            ? 'bg-red-100 text-red-700'
                            : tc.priority === 'P1'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {tc.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-xs truncate">
                      {tc.preconditions || '-'}
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-xs truncate">
                      {tc.expected_result}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleEditStart(tc)}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 text-xs"
                        title="Edit test case"
                      >
                        <Edit2 size={14} /> Edit
                      </button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Expanded view for mobile */}
      <div className="md:hidden space-y-4 p-4">
        {testCases.map(tc => (
          <div key={tc.id} className="border border-gray-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2 justify-between">
              <span className="font-mono font-bold text-blue-600 text-sm">{tc.id}</span>
              <span
                className={`px-2 py-1 text-xs font-semibold rounded ${
                  tc.priority === 'P0'
                    ? 'bg-red-100 text-red-700'
                    : tc.priority === 'P1'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-green-100 text-green-700'
                }`}
              >
                {tc.priority}
              </span>
            </div>
            <p className="font-semibold text-gray-900 text-sm">{tc.title}</p>
            <div className="space-y-1 text-xs text-gray-600">
              <p><span className="font-semibold">Type:</span> {tc.type}</p>
              <p><span className="font-semibold">Expected:</span> {tc.expected_result}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
