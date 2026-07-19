import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "skeleton rounded-md bg-slate-200 dark:bg-slate-800",
        className
      )}
    />
  );
}
