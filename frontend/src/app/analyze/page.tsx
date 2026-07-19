"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Braces, FileArchive, Github, Loader2, UploadCloud, X } from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { formatBytes, cn } from "@/lib/utils";

type Mode = "code_snippet" | "github_url" | "zip_file";

const SAMPLE = `def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b`;

export default function AnalyzePage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("code_snippet");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadPct, setUploadPct] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const submit = async () => {
    setError(null);
    setLoading(true);
    try {
      let jobId: string;
      if (mode === "zip_file") {
        if (!file) throw new Error("Please choose a .zip file");
        setUploadPct(0);
        const res = await api.uploadZip(file, setUploadPct);
        jobId = res.job_id;
      } else {
        if (!text.trim()) throw new Error("Please enter some input");
        const res = await api.startAnalysis(mode, text.trim());
        jobId = res.job_id;
      }
      router.push(`/results/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start analysis");
      setLoading(false);
      setUploadPct(null);
    }
  };

  const pickFile = (f: File | null) => {
    if (f && !f.name.toLowerCase().endsWith(".zip")) {
      setError("Only .zip files are allowed");
      return;
    }
    setError(null);
    setFile(f);
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-14 sm:px-6">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          Analyze code
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Choose an input and we&apos;ll generate, run, and measure tests for it.
        </p>

        <Card className="mt-8 p-6">
          <Tabs
            tabs={[
              { id: "code_snippet", label: "Code" },
              { id: "github_url", label: "GitHub" },
              { id: "zip_file", label: "ZIP" },
            ]}
            active={mode}
            onChange={(id) => {
              setMode(id as Mode);
              setError(null);
            }}
          />

          <div className="pt-6">
            {mode === "code_snippet" && (
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label htmlFor="code" className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    <Braces size={14} className="mr-1 inline" /> Python code
                  </label>
                  <button
                    type="button"
                    onClick={() => setText(SAMPLE)}
                    className="text-xs text-indigo-600 hover:underline dark:text-indigo-400"
                  >
                    Insert sample
                  </button>
                </div>
                <textarea
                  id="code"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={SAMPLE}
                  className="h-56 w-full resize-none rounded-lg border border-slate-300 bg-white p-4 font-mono text-sm text-slate-900 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                />
              </div>
            )}

            {mode === "github_url" && (
              <div>
                <label htmlFor="repo" className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
                  <Github size={14} className="mr-1 inline" /> Public repository URL
                </label>
                <input
                  id="repo"
                  type="url"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="https://github.com/user/repo"
                  className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                />
                <p className="mt-2 text-xs text-slate-500">github.com, gitlab.com, or bitbucket.org over HTTPS.</p>
              </div>
            )}

            {mode === "zip_file" && (
              <div>
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragging(false);
                    pickFile(e.dataTransfer.files?.[0] ?? null);
                  }}
                  onClick={() => inputRef.current?.click()}
                  className={cn(
                    "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition-colors",
                    dragging
                      ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/30"
                      : "border-slate-300 hover:border-indigo-400 dark:border-slate-700"
                  )}
                >
                  <UploadCloud className="text-slate-400" size={28} />
                  <p className="mt-3 text-sm font-medium text-slate-700 dark:text-slate-200">
                    Drag & drop a .zip, or click to browse
                  </p>
                  <p className="mt-1 text-xs text-slate-500">Max 15 MB</p>
                  <input
                    ref={inputRef}
                    type="file"
                    accept=".zip"
                    className="hidden"
                    onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
                  />
                </div>

                {file && (
                  <div className="mt-3 flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 dark:border-slate-800 dark:bg-slate-900">
                    <div className="flex items-center gap-2 text-sm">
                      <FileArchive size={16} className="text-indigo-500" />
                      <span className="text-slate-700 dark:text-slate-200">{file.name}</span>
                      <span className="text-slate-400">{formatBytes(file.size)}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setFile(null)}
                      className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                      aria-label="Remove file"
                    >
                      <X size={16} />
                    </button>
                  </div>
                )}

                {uploadPct !== null && (
                  <div className="mt-3">
                    <div className="mb-1 flex justify-between text-xs text-slate-500">
                      <span>Uploading…</span>
                      <span>{uploadPct}%</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                      <div className="h-full bg-indigo-500 transition-all" style={{ width: `${uploadPct}%` }} />
                    </div>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div role="alert" className="mt-4 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/30 dark:text-rose-300">
                {error}
              </div>
            )}

            <Button onClick={submit} disabled={loading} size="lg" className="mt-6 w-full">
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" /> Starting analysis…
                </>
              ) : (
                "Generate tests"
              )}
            </Button>
          </div>
        </Card>
      </main>
      <Footer />
    </div>
  );
}
