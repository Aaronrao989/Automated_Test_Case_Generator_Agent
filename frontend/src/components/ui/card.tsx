import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div
      className={cn(
        "rounded-xl border border-slate-200 bg-white shadow-sm",
        "dark:border-slate-800 dark:bg-slate-900/60",
        className
      )}
    >
      {children}
    </div>
  );
}

export function Stat({
  label,
  value,
  accent = "text-indigo-500",
}: {
  label: string;
  value: ReactNode;
  accent?: string;
}) {
  return (
    <Card className="p-5">
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <p className={cn("mt-1 text-3xl font-semibold tabular-nums", accent)}>{value}</p>
    </Card>
  );
}
