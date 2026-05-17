'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Upload, ArrowLeft, Loader } from 'lucide-react';

export default function UploadPage() {

  const [file, setFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);

  const [jobId, setJobId] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);


  // ==========================================================
  // FILE CHANGE
  // ==========================================================

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {

    if (e.target.files) {

      setFile(e.target.files[0]);

      setError(null);
    }
  };


  // ==========================================================
  // ZIP FILE UPLOAD
  // ==========================================================

  const handleSubmit = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    if (!file) {

      setError('Please select a file');

      return;
    }

    setLoading(true);

    setError(null);

    try {

      const formData = new FormData();

      formData.append('file', file);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/upload`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {

        const errorData = await response.json();

        throw new Error(
          errorData.detail || 'Upload failed'
        );
      }

      const data = await response.json();

      setJobId(data.job_id);

      setFile(null);

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : 'Upload failed'
      );

    } finally {

      setLoading(false);
    }
  };


  // ==========================================================
  // URL / CODE / USER STORY SUBMIT
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

    const sourceType = (
      formData.get('source_type') as string
    );

    if (!url) {

      setError(
        'Please enter a URL or description'
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

            source_type: sourceType,

            source_data: url,
          }),
        }
      );

      if (!response.ok) {

        const errorData = await response.json();

        console.error(errorData);

        throw new Error(
          errorData.detail || 'Analysis start failed'
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
            Upload Repository
          </h2>

        </div>

      </nav>


      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">

        {jobId ? (

          <div className="bg-green-500/20 border border-green-500 rounded-lg p-8 text-center">

            <h2 className="text-2xl font-bold text-white mb-4">
              ✓ Analysis Started!
            </h2>

            <p className="text-slate-300 mb-6">

              Your analysis job has been created.

              <br />

              Job ID:

              <code className="bg-slate-800 px-3 py-1 rounded ml-2">
                {jobId}
              </code>

            </p>

            <p className="text-slate-400 mb-6">
              Analysis is processing.
            </p>

            <div className="flex gap-4 justify-center">

              <Link
                href="/dashboard"
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
              >
                View Dashboard
              </Link>

              <button
                onClick={() => setJobId(null)}
                className="px-6 py-2 border border-purple-600 text-purple-400 hover:bg-purple-600/10 rounded-lg transition"
              >
                Upload Another
              </button>

            </div>

          </div>

        ) : (

          <div className="grid md:grid-cols-2 gap-8">

            {/* FILE UPLOAD */}

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">

              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">

                <Upload
                  size={24}
                  className="text-purple-400"
                />

                Upload ZIP File

              </h3>

              <form
                onSubmit={handleSubmit}
                className="space-y-4"
              >

                <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-purple-500 transition cursor-pointer">

                  <input
                    type="file"
                    accept=".zip"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-input"
                  />

                  <label
                    htmlFor="file-input"
                    className="cursor-pointer"
                  >

                    <div className="text-slate-400">

                      <p className="text-lg font-semibold text-white mb-2">

                        {file
                          ? file.name
                          : 'Click to upload or drag and drop'}

                      </p>

                      <p className="text-sm">
                        ZIP files only (Max 100MB)
                      </p>

                    </div>

                  </label>

                </div>

                <button
                  type="submit"
                  disabled={!file || loading}
                  className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
                >

                  {loading ? (
                    <>
                      <Loader
                        size={20}
                        className="animate-spin"
                      />
                      Uploading...
                    </>
                  ) : (
                    'Upload & Analyze'
                  )}

                </button>

              </form>

            </div>


            {/* URL / STORY / CODE */}

            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">

              <h3 className="text-xl font-bold text-white mb-6">
                Repository / Prompt Input
              </h3>

              <form
                onSubmit={handleUrlSubmit}
                className="space-y-4"
              >

                <div>

                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Repository Type
                  </label>

                  <select
                    name="source_type"
                    defaultValue="github_url"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                  >

                    <option value="github_url">
                      GitHub URL
                    </option>

                    <option value="user_story">
                      User Story / Specification
                    </option>

                    <option value="code_snippet">
                      Code Snippet
                    </option>

                  </select>

                </div>


                <div>

                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Enter URL or Description
                  </label>

                  <textarea
                    name="url"
                    placeholder="e.g., https://github.com/pallets/flask"
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500 h-32 resize-none"
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