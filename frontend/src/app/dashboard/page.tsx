'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Loader, BarChart3 } from 'lucide-react';

interface AnalysisResult {
  job_id: string;
  status: string;
  message?: string;
  created_at?: string;
  structure?: any;
  functions?: any[];
  edge_cases?: any[];
  tests?: any[];
  coverage?: any;
}

export default function DashboardPage() {
  const [jobId, setJobId] = useState<string>('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId) {
      setError('Please enter a Job ID');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/${jobId}`);

      if (response.status === 202) {
        setError('Analysis still in progress. Please wait a few moments and try again.');
        setLoading(false);
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch results');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch results. Make sure the Job ID is correct and backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2 text-slate-300 hover:text-white">
            <ArrowLeft size={20} /> Back
          </Link>
          <h2 className="text-2xl font-bold text-white">Analysis Dashboard</h2>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {!result ? (
          <div className="max-w-2xl mx-auto bg-slate-800/50 border border-slate-700 rounded-lg p-8">
            <h3 className="text-2xl font-bold text-white mb-6">Check Analysis Status</h3>
            <form onSubmit={handleCheckStatus} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Job ID
                </label>
                <input
                  type="text"
                  placeholder="e.g., 06b81fd1-2646-41ed-8e24-8d1098bcef16"
                  value={jobId}
                  onChange={(e) => setJobId(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Checking Status...
                  </>
                ) : (
                  'Check Status'
                )}
              </button>
            </form>
            {error && (
              <div className="mt-4 bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-200">
                {error}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {/* Status Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                  <BarChart3 size={28} className="text-purple-400" />
                  Analysis Results
                </h3>
                <span className={`px-4 py-2 rounded-full font-semibold ${
                  result.status === 'COMPLETED'
                    ? 'bg-green-500/20 text-green-300'
                    : result.status === 'IN_PROGRESS'
                    ? 'bg-blue-500/20 text-blue-300'
                    : 'bg-yellow-500/20 text-yellow-300'
                }`}>
                  {result.status}
                </span>
              </div>
              <p className="text-slate-400">Job ID: <code className="bg-slate-700 px-2 py-1 rounded">{result.job_id}</code></p>
            </div>

            {/* Results Grid */}
            {result.status === 'COMPLETED' ? (
              <div className="space-y-8">
                {/* Summary Stats */}
                <div className="grid md:grid-cols-4 gap-4">
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Languages Detected</h4>
                    <p className="text-3xl font-bold text-purple-400">
                      {result.structure?.languages ? Object.keys(result.structure.languages).length : 0}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Edge Cases Found</h4>
                    <p className="text-3xl font-bold text-orange-400">{result.edge_cases?.length || 0}</p>
                  </div>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Tests Generated</h4>
                    <p className="text-3xl font-bold text-green-400">{result.tests?.length || 0}</p>
                  </div>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Functions Analyzed</h4>
                    <p className="text-3xl font-bold text-blue-400">{result.structure?.functions?.length || 0}</p>
                  </div>
                </div>

                {/* Languages */}
                {result.structure?.languages && Object.keys(result.structure.languages).length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
                    <h4 className="text-xl font-bold text-white mb-4">Languages Detected</h4>
                    <div className="grid md:grid-cols-3 gap-4">
                      {Object.entries(result.structure.languages).map(([lang, count]: [string, any]) => (
                        <div key={lang} className="bg-slate-700/50 p-4 rounded-lg">
                          <p className="text-slate-300 capitalize">{lang}</p>
                          <p className="text-2xl font-bold text-purple-300">{count}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Edge Cases */}
                {result.edge_cases && result.edge_cases.length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
                    <h4 className="text-xl font-bold text-white mb-4">Edge Cases Identified</h4>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {result.edge_cases.slice(0, 20).map((edgeCase: any, idx: number) => (
                        <div key={idx} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                          <p className="font-semibold text-orange-300 mb-2">{edgeCase.edge_case}</p>
                          <p className="text-sm text-slate-300">{edgeCase.description}</p>
                          {edgeCase.test_code && (
                            <pre className="mt-2 bg-slate-900 p-2 rounded text-xs text-slate-300 overflow-x-auto">
                              {edgeCase.test_code}
                            </pre>
                          )}
                        </div>
                      ))}
                      {result.edge_cases.length > 20 && (
                        <p className="text-slate-400 text-sm">... and {result.edge_cases.length - 20} more edge cases</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Generated Tests */}
                {result.tests && result.tests.length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
                    <h4 className="text-xl font-bold text-white mb-4">Tests Generated</h4>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {result.tests.slice(0, 10).map((test: any, idx: number) => (
                        <div key={idx} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                          <div className="flex items-start justify-between mb-2">
                            <p className="font-semibold text-green-300">{test.target_function}</p>
                            <span className="text-xs bg-slate-600 px-2 py-1 rounded text-slate-200">
                              {test.test_type || 'unit'}
                            </span>
                          </div>
                          <pre className="bg-slate-900 p-2 rounded text-xs text-slate-300 overflow-x-auto max-h-32">
                            {test.content?.substring(0, 500) || test}
                          </pre>
                        </div>
                      ))}
                      {result.tests.length > 10 && (
                        <p className="text-slate-400 text-sm">... and {result.tests.length - 10} more tests</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Coverage Report */}
                {result.coverage && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
                    <h4 className="text-xl font-bold text-white mb-4">Coverage Report</h4>
                    {result.coverage.total_coverage !== undefined && (
                      <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-slate-300">Total Coverage</span>
                          <span className="text-2xl font-bold text-blue-300">{(result.coverage.total_coverage).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-600 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${Math.min(result.coverage.total_coverage, 100)}%` }}
                          />
                        </div>
                      </div>
                    )}
                    <pre className="bg-slate-900 rounded-lg p-4 text-slate-300 overflow-auto max-h-96 text-sm">
                      {JSON.stringify(result.coverage, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-blue-500/20 border border-blue-500 rounded-lg p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Loader size={24} className="animate-spin text-blue-400" />
                </div>
                <p className="text-blue-200">Analysis is still in progress. Please wait a few moments and refresh.</p>
                <button
                  onClick={() => setResult(null)}
                  className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                >
                  Check Again
                </button>
              </div>
            )}

            <button
              onClick={() => setResult(null)}
              className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
            >
              Check Another Job
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
