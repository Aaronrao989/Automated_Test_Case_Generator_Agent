'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function TestsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2 text-slate-300 hover:text-white">
            <ArrowLeft size={20} /> Back
          </Link>
          <h2 className="text-2xl font-bold text-white">Generated Tests</h2>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-12 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">Tests Viewer</h3>
          <p className="text-slate-400 mb-8">
            View and download generated test cases from your analysis.
          </p>
          <p className="text-slate-500">Coming soon...</p>
          <Link 
            href="/"
            className="mt-8 inline-block px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
          >
            Go Home
          </Link>
        </div>
      </div>
    </div>
  );
}
