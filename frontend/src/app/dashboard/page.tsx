'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Loader,
  BarChart3
} from 'lucide-react';


interface AnalysisResult {

  job_id: string;

  status: string;

  message?: string;

  created_at?: string;

  updated_at?: string;

  source_type?: string;

  structure?: any;

  functions?: any[];

  edge_cases?: any[];

  tests?: any[];

  coverage?: any;

  error?: string;
}


export default function DashboardPage() {

  const [jobId, setJobId] = useState<string>('');

  const [result, setResult] =
    useState<AnalysisResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  // ==========================================================
  // CHECK STATUS
  // ==========================================================

  const handleCheckStatus = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    if (!jobId.trim()) {

      setError('Please enter a Job ID');

      return;
    }

    setLoading(true);

    setError(null);

    try {

      const response = await fetch(

        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${jobId}`,

        {
          method: 'GET',
        }
      );

      if (!response.ok) {

        const errorData =
          await response.json().catch(
            () => ({})
          );

        throw new Error(
          errorData.detail ||
          'Failed to fetch results'
        );
      }

      const data = await response.json();

      setResult(data);

    } catch (err) {

      setError(

        err instanceof Error
          ? err.message
          : 'Failed to fetch results'
      );

    } finally {

      setLoading(false);
    }
  };


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">

      {/* NAVIGATION */}

      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">

          <Link
            href="/"
            className="flex items-center gap-2 text-slate-300 hover:text-white"
          >

            <ArrowLeft size={20} />

            Back

          </Link>

          <h2 className="text-2xl font-bold text-white">
            Analysis Dashboard
          </h2>

        </div>

      </nav>


      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">

        {!result ? (

          <div className="max-w-2xl mx-auto bg-slate-800/50 border border-slate-700 rounded-lg p-8">

            <h3 className="text-2xl font-bold text-white mb-6">
              Check Analysis Status
            </h3>

            <form
              onSubmit={handleCheckStatus}
              className="space-y-4"
            >

              <div>

                <label className="block text-sm font-medium text-slate-300 mb-2">

                  Job ID

                </label>

                <input
                  type="text"

                  placeholder="e.g., 06b81fd1-2646-41ed-8e24-8d1098bcef16"

                  value={jobId}

                  onChange={(e) =>
                    setJobId(e.target.value)
                  }

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
                    <Loader
                      size={20}
                      className="animate-spin"
                    />

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

            {/* STATUS */}

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">

              <div className="flex items-center justify-between mb-6">

                <h3 className="text-2xl font-bold text-white flex items-center gap-2">

                  <BarChart3
                    size={28}
                    className="text-purple-400"
                  />

                  Analysis Results

                </h3>


                <span
                  className={`px-4 py-2 rounded-full font-semibold ${
                    result.status === 'COMPLETED'
                      ? 'bg-green-500/20 text-green-300'
                      : result.status === 'FAILED'
                      ? 'bg-red-500/20 text-red-300'
                      : 'bg-blue-500/20 text-blue-300'
                  }`}
                >

                  {result.status}

                </span>

              </div>


              <p className="text-slate-400">

                Job ID:

                <code className="bg-slate-700 px-2 py-1 rounded ml-2">

                  {result.job_id}

                </code>

              </p>

            </div>


            {/* FAILED */}

            {result.status === 'FAILED' && (

              <div className="bg-red-500/20 border border-red-500 rounded-lg p-6">

                <h4 className="text-xl font-bold text-red-200 mb-3">
                  Analysis Failed
                </h4>

                <p className="text-red-100">

                  {result.error || 'Unknown error'}

                </p>

              </div>
            )}


            {/* IN PROGRESS */}

            {(result.status === 'PENDING' ||
              result.status === 'IN_PROGRESS') && (

              <div className="bg-blue-500/20 border border-blue-500 rounded-lg p-6 text-center">

                <div className="flex items-center justify-center gap-2 mb-4">

                  <Loader
                    size={24}
                    className="animate-spin text-blue-400"
                  />

                </div>

                <p className="text-blue-200">

                  Analysis is still in progress.
                  Please wait a few moments and try again.

                </p>

              </div>
            )}


            {/* COMPLETED */}

            {result.status === 'COMPLETED' && (

              <div className="space-y-8">

                {/* SUMMARY */}

                <div className="grid md:grid-cols-4 gap-4">

                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">

                    <h4 className="text-sm font-medium text-slate-300 mb-2">
                      Languages
                    </h4>

                    <p className="text-3xl font-bold text-purple-400">

                      {result.structure?.languages
                        ? Object.keys(
                            result.structure.languages
                          ).length
                        : 0}

                    </p>

                  </div>


                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">

                    <h4 className="text-sm font-medium text-slate-300 mb-2">
                      Edge Cases
                    </h4>

                    <p className="text-3xl font-bold text-orange-400">

                      {result.edge_cases?.length || 0}

                    </p>

                  </div>


                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">

                    <h4 className="text-sm font-medium text-slate-300 mb-2">
                      Tests
                    </h4>

                    <p className="text-3xl font-bold text-green-400">

                      {result.tests?.length || 0}

                    </p>

                  </div>


                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">

                    <h4 className="text-sm font-medium text-slate-300 mb-2">
                      Functions
                    </h4>

                    <p className="text-3xl font-bold text-blue-400">

                      {result.structure?.functions?.length || 0}

                    </p>

                  </div>

                </div>


                {/* RAW RESULT */}

                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">

                  <h4 className="text-xl font-bold text-white mb-4">
                    Complete Analysis Result
                  </h4>

                  <pre className="bg-slate-900 rounded-lg p-4 text-slate-300 overflow-auto max-h-[700px] text-sm">

                    {JSON.stringify(
                      result,
                      null,
                      2
                    )}

                  </pre>

                </div>

              </div>
            )}


            <button
              onClick={() => {

                setResult(null);

                setJobId('');

                setError(null);
              }}

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