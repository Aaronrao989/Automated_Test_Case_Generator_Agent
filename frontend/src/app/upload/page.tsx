'use client';

import { useState } from 'react';
import Link from 'next/link';

import {
  ArrowLeft,
  Loader,
  Copy,
  Check,
  Github,
  Code2
} from 'lucide-react';


export default function UploadPage() {

  const [loading, setLoading] = useState(false);

  const [jobId, setJobId] =
    useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [copied, setCopied] =
    useState(false);

  const [sourceType, setSourceType] =
    useState('github_url');


  // ==========================================================
  // COPY JOB ID
  // ==========================================================

  const copyJobId = async () => {

    if (!jobId) return;

    try {

      await navigator.clipboard.writeText(jobId);

      setCopied(true);

      setTimeout(() => {

        setCopied(false);

      }, 2000);

    } catch {

      console.error('Copy failed');
    }
  };


  // ==========================================================
  // URL / CODE SUBMIT
  // ==========================================================

  const handleUrlSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {

    e.preventDefault();

    const formData = new FormData(
      e.currentTarget
    );

    const url = (
      formData.get('url') as string
    )?.trim();

    const selectedSourceType = (
      formData.get('source_type') as string
    );

    if (!url) {

      setError(
        'Please enter a GitHub URL or code snippet'
      );

      return;
    }

    setLoading(true);

    setError(null);

    try {

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/start`,
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json'
          },

          body: JSON.stringify({

            source_type: selectedSourceType,

            source_data: url,
          }),
        }
      );

      if (!response.ok) {

        const errorData =
          await response.json();

        console.error(errorData);

        throw new Error(
          errorData.detail ||
          'Analysis start failed'
        );
      }

      const data = await response.json();

      setJobId(data.job_id);

    } catch (err) {

      setError(

        err instanceof Error
          ? err.message
          : 'Failed to start analysis'
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
            Repository Analysis
          </h2>

        </div>

      </nav>


      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">

        {jobId ? (

          <div className="bg-green-500/20 border border-green-500 rounded-lg p-8 text-center">

            <h2 className="text-2xl font-bold text-white mb-4">
              ✓ Analysis Started!
            </h2>


            <div className="text-slate-300 mb-6">

              <p className="mb-4">
                Your analysis job has been created successfully.
              </p>

              <div className="flex items-center justify-center gap-3 flex-wrap">

                <span className="text-slate-400">
                  Job ID:
                </span>

                <code className="bg-slate-800 px-3 py-2 rounded border border-slate-700 text-green-300">

                  {jobId}

                </code>

                <button
                  onClick={copyJobId}
                  className="flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white transition"
                >

                  {copied ? (
                    <>
                      <Check size={16} />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy size={16} />
                      Copy
                    </>
                  )}

                </button>

              </div>

            </div>


            <div className="mb-6">

              <p className="text-slate-400 mb-2">
                Analysis is processing.
              </p>

              <p className="text-sm text-slate-500">
                Copy the Job ID and paste it into the Dashboard
                to track analysis results.
              </p>

            </div>


            <div className="flex gap-4 justify-center">

              <Link
                href="/dashboard"
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
              >

                View Dashboard

              </Link>

              <button
                onClick={() => {

                  setJobId(null);

                  setError(null);
                }}

                className="px-6 py-2 border border-purple-600 text-purple-400 hover:bg-purple-600/10 rounded-lg transition"
              >

                Analyze Another

              </button>

            </div>

          </div>

        ) : (

          <div className="max-w-3xl mx-auto">

            {/* URL / CODE */}

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">

              <h3 className="text-xl font-bold text-white mb-6">
                Repository / Code Input
              </h3>


              <form
                onSubmit={handleUrlSubmit}
                className="space-y-4"
              >

                <div>

                  <label className="block text-sm font-medium text-slate-300 mb-2">

                    Analysis Type

                  </label>

                  <select
                    name="source_type"

                    value={sourceType}

                    onChange={(e) =>
                      setSourceType(
                        e.target.value
                      )
                    }

                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                  >

                    <option value="github_url">

                      GitHub Repository URL

                    </option>

                    <option value="code_snippet">

                      Source Code Snippet

                    </option>

                  </select>

                </div>


                <div>

                  <label className="block text-sm font-medium text-slate-300 mb-2">

                    Enter Repository URL or Source Code

                  </label>

                  <textarea
                    name="url"

                    placeholder={
                      sourceType === 'github_url'
                        ? 'e.g., https://github.com/username/repository'
                        : 'Paste your Python, JavaScript, or TypeScript code here'
                    }

                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-purple-500 h-40 resize-none"
                  />


                  {sourceType === 'github_url' ? (

                    <p className="mt-2 text-sm text-slate-400 flex items-center gap-2">

                      <Github size={14} />

                      Expected format:
                      https://github.com/username/repository

                    </p>

                  ) : (

                    <p className="mt-2 text-sm text-slate-400 flex items-center gap-2">

                      <Code2 size={14} />

                      Supported formats:
                      Python, JavaScript, and TypeScript

                    </p>

                  )}

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

                      Starting Analysis...
                    </>
                  ) : (
                    'Start Analysis'
                  )}

                </button>

              </form>

            </div>

          </div>
        )}


        {error && (

          <div className="mt-8 bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-200">

            {error}

          </div>
        )}

      </div>

    </div>
  );
}