"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Clock, Loader2, Search, Trash2 } from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge, statusTone } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { RecentJob } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<RecentJob[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lookup, setLookup] = useState("");

  const load = useCallback(async () => {
    try {
      setJobs(await api.listRecent(30));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const remove = async (id: string) => {
    await api.deleteJob(id).catch(() => undefined);
    setJobs((prev) => prev?.filter((j) => j.job_id !== id) ?? null);
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-12 sm:px-6">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">History</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Recent analyses</p>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (lookup.trim()) router.push(`/results/${lookup.trim()}`);
            }}
            className="flex gap-2"
          >
            <div className="relative">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={lookup}
                onChange={(e) => setLookup(e.target.value)}
                placeholder="Open by Job ID"
                className="rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-indigo-500 dark:border-slate-700 dark:bg-slate-950"
              />
            </div>
            <Button type="submit" variant="secondary" size="sm">
              Open
            </Button>
          </form>
        </div>

        {error && (
          <Card className="p-6 text-sm text-rose-600 dark:text-rose-400">{error}</Card>
        )}

        {!jobs && !error && (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-20" />
            ))}
          </div>
        )}

        {jobs && jobs.length === 0 && (
          <Card className="p-12 text-center">
            <p className="text-slate-500 dark:text-slate-400">No analyses yet.</p>
            <Button className="mt-4" onClick={() => router.push("/analyze")}>
              Analyze your first snippet <ArrowRight size={16} />
            </Button>
          </Card>
        )}

        {jobs && jobs.length > 0 && (
          <div className="space-y-3">
            {jobs.map((job) => (
              <Card key={job.job_id} className="flex items-center justify-between gap-4 p-4">
                <Link href={`/results/${job.job_id}`} className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <Badge tone={statusTone(job.status)}>
                      {job.status === "IN_PROGRESS" || job.status === "PENDING" ? (
                        <Loader2 size={12} className="animate-spin" />
                      ) : null}
                      {job.status}
                    </Badge>
                    <span className="truncate text-sm text-slate-500 dark:text-slate-400">
                      {job.source_type}
                    </span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-3 text-xs text-slate-400">
                    <span className="inline-flex items-center gap-1">
                      <Clock size={12} /> {timeAgo(job.created_at)}
                    </span>
                    {job.stats && (
                      <span>
                        {job.stats.test_cases} tests · {job.stats.functions_analyzed} functions
                      </span>
                    )}
                    <code className="truncate">{job.job_id.slice(0, 8)}</code>
                  </div>
                </Link>
                <button
                  type="button"
                  onClick={() => remove(job.job_id)}
                  className="shrink-0 rounded-lg p-2 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-500 dark:hover:bg-rose-950/30"
                  aria-label="Delete analysis"
                >
                  <Trash2 size={16} />
                </button>
              </Card>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
