"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "next/navigation";
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Download,
  FileCode2,
  Package,
  Search,
  Wrench,
} from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import { Card, Stat } from "@/components/ui/card";
import { Badge, statusTone } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabPanel } from "@/components/ui/tabs";
import { CodeBlock } from "@/components/ui/code-block";
import { Skeleton } from "@/components/ui/skeleton";
import { StageProgress, CoverageBar } from "@/components/ui/progress";
import { api } from "@/lib/api";
import { createZip } from "@/lib/zip";
import { download } from "@/lib/utils";
import type { AnalysisResult, Stage } from "@/lib/types";

const IN_FLIGHT = new Set(["PENDING", "IN_PROGRESS"]);

export default function ResultsPage() {
  const params = useParams();
  const jobId = params.jobId as string;
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState("overview");
  const startedAt = useRef<string>(new Date().toISOString());
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const poll = useCallback(async () => {
    try {
      const data = await api.getResult(jobId);
      setResult(data);
      if (IN_FLIGHT.has(data.status)) {
        timer.current = setTimeout(poll, 2500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load results");
    }
  }, [jobId]);

  useEffect(() => {
    poll();
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [poll]);

  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12 sm:px-6">
        {error ? (
          <ErrorState message={error} />
        ) : !result ? (
          <LoadingState />
        ) : IN_FLIGHT.has(result.status) ? (
          <Card className="mx-auto max-w-lg p-8">
            <StageProgress stage={(result.stage as Stage) ?? "queued"} startedAt={startedAt.current} />
          </Card>
        ) : result.status === "FAILED" ? (
          <ErrorState message={result.error ?? "Analysis failed"} />
        ) : (
          <CompletedView result={result} tab={tab} setTab={setTab} />
        )}
      </main>
      <Footer />
    </div>
  );
}

function CompletedView({
  result,
  tab,
  setTab,
}: {
  result: AnalysisResult;
  tab: string;
  setTab: (t: string) => void;
}) {
  const stats = result.stats;
  const tests = result.tests ?? [];
  const edgeCases = result.edge_cases ?? [];
  const functions = result.structure?.functions ?? [];
  const coverage = result.coverage;

  const downloadAllTests = () => {
    const files = tests.map((t, i) => ({
      name: `test_${t.target_function || i}.py`,
      content: t.content,
    }));
    if (files.length) download("generated-tests.zip", createZip(files), "application/zip");
  };

  const trace = result.agent_trace ?? [];
  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "agent", label: "Agent", count: trace.length },
    { id: "functions", label: "Functions", count: functions.length },
    { id: "edge", label: "Edge cases", count: edgeCases.length },
    { id: "tests", label: "Tests", count: tests.length },
    { id: "coverage", label: "Coverage" },
    { id: "execution", label: "Execution", count: result.test_results?.length ?? 0 },
  ];

  return (
    <div className="animate-fade-in">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Analysis results</h1>
          <code className="text-xs text-slate-400">{result.job_id}</code>
        </div>
        <Badge tone="success" className="px-3 py-1 text-sm">
          <CheckCircle2 size={14} /> Completed
        </Badge>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Functions" value={stats?.functions_analyzed ?? functions.length} accent="text-indigo-500" />
        <Stat label="Test cases" value={stats?.test_cases ?? 0} accent="text-emerald-500" />
        <Stat label="Edge cases" value={edgeCases.length} accent="text-amber-500" />
        <Stat label="Coverage" value={`${coverage?.total_coverage ?? 0}%`} accent="text-violet-500" />
      </div>

      <Tabs tabs={tabs} active={tab} onChange={setTab} />

      {tab === "overview" && (
        <TabPanel>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Files scanned" value={stats?.files_scanned ?? 1} />
            <Stat label="Lines of code" value={stats?.total_loc ?? 0} />
            <Stat label="Functions found" value={stats?.functions_found ?? 0} />
            <Stat label="Test modules" value={stats?.test_modules ?? tests.length} />
          </div>
          {result.structure?.languages && Object.keys(result.structure.languages).length > 0 && (
            <Card className="mt-4 p-6">
              <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">Languages detected</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(result.structure.languages).map(([lang, count]) => (
                  <Badge key={lang} tone="info">
                    {lang} · {count}
                  </Badge>
                ))}
              </div>
            </Card>
          )}
        </TabPanel>
      )}

      {tab === "agent" && (
        <TabPanel>
          <Card className="p-6">
            <div className="mb-5 flex items-center gap-2">
              <Wrench size={16} className="text-indigo-500" />
              <h2 className="font-semibold text-slate-900 dark:text-white">
                Agent tool trace
              </h2>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {trace.length} tools invoked
              </span>
            </div>
            <ol className="relative space-y-4 border-l border-slate-200 pl-6 dark:border-slate-800">
              {trace.map((step, i) => (
                <li key={i} className="relative">
                  <span
                    className={`absolute -left-[27px] top-1 h-3 w-3 rounded-full ring-4 ring-white dark:ring-slate-900 ${
                      step.status === "ok" ? "bg-emerald-500" : "bg-rose-500"
                    }`}
                  />
                  <div className="flex flex-wrap items-center gap-2">
                    <code className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                      {step.tool}
                    </code>
                    <span className="text-xs tabular-nums text-slate-400">{step.duration}s</span>
                  </div>
                  <p className="text-xs text-slate-400">{step.description}</p>
                  <p className="mt-0.5 text-sm text-slate-700 dark:text-slate-300">{step.summary}</p>
                </li>
              ))}
            </ol>
          </Card>
        </TabPanel>
      )}

      {tab === "functions" && (
        <TabPanel>
          <SearchableList
            items={functions.map((f) => `${f.name}${f.file ? `  —  ${f.file}` : ""}`)}
            empty="No functions detected."
            icon={<FileCode2 size={15} className="text-indigo-500" />}
          />
        </TabPanel>
      )}

      {tab === "edge" && (
        <TabPanel>
          {edgeCases.length === 0 ? (
            <EmptyState message="No edge cases identified." />
          ) : (
            <div className="space-y-2">
              {edgeCases.map((ec, i) => (
                <Card key={i} className="flex items-start justify-between gap-3 p-4">
                  <div>
                    <Badge tone="warning">{ec.type}</Badge>
                    <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">{ec.description}</p>
                  </div>
                </Card>
              ))}
              <CopyButton
                text={edgeCases.map((e) => `- [${e.type}] ${e.description}`).join("\n")}
                label="Copy edge cases"
              />
            </div>
          )}
        </TabPanel>
      )}

      {tab === "tests" && (
        <TabPanel>
          <TestsPanel tests={tests} onDownloadAll={downloadAllTests} />
        </TabPanel>
      )}

      {tab === "coverage" && (
        <TabPanel>
          <Card className="p-6">
            {coverage?.executed === false ? (
              <div className="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">
                <AlertTriangle size={18} className="mt-0.5 shrink-0" />
                <p>
                  Tests couldn&apos;t execute — the analyzed code likely imports third-party
                  dependencies that aren&apos;t installed in the runner. Coverage is available for
                  self-contained, standard-library code.
                </p>
              </div>
            ) : (
              <>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-slate-600 dark:text-slate-300">Total coverage</span>
                  <span className="text-2xl font-semibold text-violet-500">
                    {coverage?.total_coverage ?? 0}%
                  </span>
                </div>
                <CoverageBar value={coverage?.total_coverage ?? 0} />
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div className="text-slate-500">
                    Covered lines:{" "}
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {coverage?.covered_lines ?? 0}
                    </span>
                  </div>
                  <div className="text-slate-500">
                    Total lines:{" "}
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {coverage?.total_lines ?? 0}
                    </span>
                  </div>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  className="mt-5"
                  onClick={() => download("coverage.json", JSON.stringify(coverage, null, 2), "application/json")}
                >
                  <Download size={15} /> Download coverage
                </Button>
              </>
            )}
          </Card>
        </TabPanel>
      )}

      {tab === "execution" && (
        <TabPanel>
          {(result.test_results?.length ?? 0) === 0 ? (
            <EmptyState message="No execution output." />
          ) : (
            <div className="space-y-3">
              {result.test_results!.map((r, i) => (
                <Card key={i} className="p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-mono text-sm text-slate-700 dark:text-slate-300">{r.file}</span>
                    <Badge tone={statusTone(r.status)}>{r.status}</Badge>
                  </div>
                  {r.output && (
                    <pre className="max-h-64 overflow-auto rounded bg-slate-100 p-3 text-xs text-slate-600 dark:bg-slate-950 dark:text-slate-400">
                      {r.output}
                    </pre>
                  )}
                </Card>
              ))}
            </div>
          )}
        </TabPanel>
      )}
    </div>
  );
}

function TestsPanel({ tests, onDownloadAll }: { tests: AnalysisResult["tests"]; onDownloadAll: () => void }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(
    () => (tests ?? []).filter((t) => t.target_function.toLowerCase().includes(query.toLowerCase())),
    [tests, query]
  );

  if (!tests || tests.length === 0) return <EmptyState message="No tests were generated." />;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by function…"
            className="rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-indigo-500 dark:border-slate-700 dark:bg-slate-950"
          />
        </div>
        <Button variant="secondary" size="sm" onClick={onDownloadAll}>
          <Package size={15} /> Download all (.zip)
        </Button>
      </div>
      {filtered.map((t, i) => (
        <div key={i}>
          <p className="mb-1.5 text-sm font-medium text-slate-700 dark:text-slate-300">{t.target_function}</p>
          <CodeBlock code={t.content} filename={`test_${t.target_function}.py`} />
        </div>
      ))}
      {filtered.length === 0 && <EmptyState message="No tests match your filter." />}
    </div>
  );
}

function SearchableList({
  items,
  empty,
  icon,
}: {
  items: string[];
  empty: string;
  icon: React.ReactNode;
}) {
  const [query, setQuery] = useState("");
  const filtered = items.filter((i) => i.toLowerCase().includes(query.toLowerCase()));
  if (items.length === 0) return <EmptyState message={empty} />;
  return (
    <div>
      <div className="relative mb-4 max-w-xs">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search…"
          className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-indigo-500 dark:border-slate-700 dark:bg-slate-950"
        />
      </div>
      <Card className="divide-y divide-slate-100 dark:divide-slate-800">
        {filtered.map((item, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2.5 font-mono text-sm text-slate-700 dark:text-slate-300">
            {icon} {item}
          </div>
        ))}
      </Card>
    </div>
  );
}

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
      }}
    >
      <Copy size={15} /> {copied ? "Copied" : label}
    </Button>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <Card className="p-10 text-center text-sm text-slate-500 dark:text-slate-400">{message}</Card>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <Card className="mx-auto max-w-lg p-8 text-center">
      <AlertTriangle className="mx-auto text-rose-500" size={28} />
      <h2 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">Something went wrong</h2>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{message}</p>
    </Card>
  );
}

function LoadingState() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-56" />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <Skeleton className="h-64" />
    </div>
  );
}
