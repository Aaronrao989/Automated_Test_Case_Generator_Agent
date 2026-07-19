"use client";

import { useState } from "react";
import { Check, Copy, Download } from "lucide-react";
import { highlightPython } from "@/lib/highlight";
import { download } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface CodeBlockProps {
  code: string;
  filename?: string;
  className?: string;
}

export function CodeBlock({ code, filename, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div
      className={cn(
        "code-block overflow-hidden rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-950",
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2 dark:border-slate-800">
        <span className="font-mono text-xs text-slate-500 dark:text-slate-400">
          {filename ?? "test.py"}
        </span>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            {copied ? "Copied" : "Copy"}
          </button>
          {filename && (
            <button
              type="button"
              onClick={() => download(filename, code, "text/x-python")}
              className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
              aria-label="Download file"
            >
              <Download size={13} />
            </button>
          )}
        </div>
      </div>
      <pre className="max-h-[26rem] overflow-auto p-4 text-xs leading-relaxed">
        <code
          className="font-mono"
          dangerouslySetInnerHTML={{ __html: highlightPython(code) }}
        />
      </pre>
    </div>
  );
}
