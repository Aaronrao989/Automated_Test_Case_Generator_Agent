"use client";

import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import type { Stage } from "@/lib/types";
import { cn } from "@/lib/utils";

const STEPS: { id: Stage; label: string }[] = [
  { id: "scanning", label: "Scanning repository" },
  { id: "extracting_functions", label: "Finding functions" },
  { id: "finding_edge_cases", label: "Finding edge cases" },
  { id: "generating_tests", label: "Generating tests" },
  { id: "running_tests", label: "Running tests" },
  { id: "computing_coverage", label: "Computing coverage" },
];

function useElapsed(startedAt?: string): string {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  if (!startedAt) return "0s";
  const secs = Math.max(0, Math.floor((now - new Date(startedAt).getTime()) / 1000));
  return secs < 60 ? `${secs}s` : `${Math.floor(secs / 60)}m ${secs % 60}s`;
}

export function StageProgress({ stage, startedAt }: { stage: Stage; startedAt?: string }) {
  const elapsed = useElapsed(startedAt);
  const currentIndex =
    stage === "completed" || stage === "queued"
      ? stage === "completed"
        ? STEPS.length
        : 0
      : STEPS.findIndex((s) => s.id === stage);
  const pct = Math.round((currentIndex / STEPS.length) * 100);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700 dark:text-slate-200">Analyzing…</span>
        <span className="tabular-nums text-slate-500 dark:text-slate-400">{elapsed}</span>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-500"
          style={{ width: `${Math.max(pct, 6)}%` }}
        />
      </div>

      <ol className="space-y-2.5">
        {STEPS.map((step, i) => {
          const done = i < currentIndex;
          const active = i === currentIndex;
          return (
            <li key={step.id} className="flex items-center gap-3 text-sm">
              <span
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded-full border",
                  done && "border-emerald-500 bg-emerald-500 text-white",
                  active && "border-indigo-500 text-indigo-500",
                  !done && !active && "border-slate-300 text-slate-300 dark:border-slate-700 dark:text-slate-600"
                )}
              >
                {done ? (
                  <Check size={12} />
                ) : active ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-current" />
                )}
              </span>
              <span
                className={cn(
                  done && "text-slate-500 dark:text-slate-400",
                  active && "font-medium text-slate-900 dark:text-slate-100",
                  !done && !active && "text-slate-400 dark:text-slate-600"
                )}
              >
                {step.label}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export function CoverageBar({ value }: { value: number }) {
  return (
    <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
      <div
        className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-700"
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
      />
    </div>
  );
}
