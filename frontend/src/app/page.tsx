'use client';

import Link from 'next/link';
import { ArrowRight, Code, Zap, BarChart3 } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">TestCaseAI</h2>
          <div className="flex gap-4">
            <Link 
              href="/upload" 
              className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            AI-Powered Test Case Generation
          </h1>
          <p className="text-xl text-slate-300 mb-12 max-w-3xl mx-auto">
            Automatically generate comprehensive test cases, identify edge cases, and analyze code coverage using AI. Turn your source code into a complete test suite in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/upload"
              className="inline-flex items-center gap-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition transform hover:scale-105"
            >
              Upload Repository <ArrowRight size={20} />
            </Link>
            <Link 
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-4 border-2 border-purple-600 text-purple-400 hover:bg-purple-600/10 font-semibold rounded-lg transition"
            >
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-white mb-16 text-center">Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 hover:border-purple-500 transition">
            <Code className="text-purple-400 mb-4" size={32} />
            <h3 className="text-xl font-bold text-white mb-3">Multi-Language Support</h3>
            <p className="text-slate-300">
              Supports Python, JavaScript, TypeScript, Java, Go, C++, and Rust. Analyze any codebase.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 hover:border-purple-500 transition">
            <Zap className="text-purple-400 mb-4" size={32} />
            <h3 className="text-xl font-bold text-white mb-3">Edge Case Detection</h3>
            <p className="text-slate-300">
              Automatically identify potential edge cases, null/empty inputs, boundary conditions, and concurrency issues.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8 hover:border-purple-500 transition">
            <BarChart3 className="text-purple-400 mb-4" size={32} />
            <h3 className="text-xl font-bold text-white mb-3">Coverage Analysis</h3>
            <p className="text-slate-300">
              Get detailed code coverage reports and suggestions for missing test scenarios.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-white mb-16 text-center">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-8">
          {['Upload', 'Analyze', 'Generate', 'Review'].map((step, i) => (
            <div key={i} className="text-center">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center text-2xl font-bold text-white mx-auto mb-4">
                {i + 1}
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{step}</h3>
              <p className="text-slate-400 text-sm">
                {i === 0 && 'Upload your repository or code snippet'}
                {i === 1 && 'AI analyzes code structure and semantics'}
                {i === 2 && 'Generate comprehensive test cases'}
                {i === 3 && 'Review and export your test suite'}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-4xl font-bold text-white mb-6">Ready to automate your testing?</h2>
        <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
          Start generating test cases now and improve your code quality.
        </p>
        <Link 
          href="/upload"
          className="inline-flex items-center gap-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition transform hover:scale-105"
        >
          Get Started Now <ArrowRight size={20} />
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900/50 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-400">
          <p>&copy; 2026 Automated Test Case Generator. Powered by AI.</p>
        </div>
      </footer>
    </div>
  );
}
