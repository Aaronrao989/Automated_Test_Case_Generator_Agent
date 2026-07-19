import Link from "next/link";
import {
  ArrowRight,
  Boxes,
  Braces,
  FileArchive,
  Github,
  Gauge,
  ListChecks,
  PlayCircle,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
} from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import { Card } from "@/components/ui/card";
import { ButtonLink } from "@/components/ui/button";

const FEATURES = [
  { icon: Braces, title: "AI test generation", desc: "Groq-powered pytest generation with happy paths, boundaries, and exceptions." },
  { icon: ScanSearch, title: "Edge-case detection", desc: "Automatic null, boundary, type-mismatch, and exception analysis per function." },
  { icon: PlayCircle, title: "Isolated execution", desc: "Every job runs in its own isolated temp dir — tests actually run, once." },
  { icon: Gauge, title: "Coverage reporting", desc: "Real line coverage collected from the same test run, not estimated." },
  { icon: ShieldCheck, title: "Safe by design", desc: "SSRF-guarded cloning, zip-slip protection, and size-limited uploads." },
  { icon: TerminalSquare, title: "Clean pytest output", desc: "Copy or download runnable test modules with syntax highlighting." },
];

const STEPS = [
  { icon: FileArchive, title: "Provide code", desc: "Paste a snippet, drop a ZIP, or point at a public repo." },
  { icon: ScanSearch, title: "We analyze", desc: "Functions are extracted and edge cases identified." },
  { icon: Sparkles, title: "AI generates", desc: "Groq writes comprehensive pytest test modules." },
  { icon: ListChecks, title: "Run & report", desc: "Tests execute and coverage is measured live." },
];

const INPUTS = [
  { icon: Braces, title: "Python code", desc: "Paste any function or module." },
  { icon: FileArchive, title: "ZIP upload", desc: "Drag & drop a project archive." },
  { icon: Github, title: "GitHub repository", desc: "Analyze a public repo by URL." },
];

const OUTPUTS = [
  { icon: TerminalSquare, title: "Generated tests" },
  { icon: Gauge, title: "Coverage report" },
  { icon: ScanSearch, title: "Edge cases" },
  { icon: ListChecks, title: "Execution results" },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Nav />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-indigo-50 to-transparent dark:from-indigo-950/30" />
        <div className="mx-auto max-w-4xl px-4 py-24 text-center sm:px-6">
          <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
            <Sparkles size={13} className="text-indigo-500" /> Powered by Groq LLMs
          </span>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl dark:text-white">
            Ship tested code,{" "}
            <span className="bg-gradient-to-r from-indigo-500 to-violet-500 bg-clip-text text-transparent">
              faster
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-300">
            TestCaseAI analyzes your Python code, finds edge cases, and generates runnable
            pytest suites — then executes them and reports real coverage. No setup required.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <ButtonLink href="/analyze" size="lg">
              Generate test cases <ArrowRight size={18} />
            </ButtonLink>
            <ButtonLink href="/dashboard" size="lg" variant="secondary">
              View history
            </ButtonLink>
          </div>
        </div>
      </section>

      {/* Features */}
      <Section id="features" title="Everything you need to test with confidence">
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <Card key={f.title} className="p-6 transition-colors hover:border-indigo-300 dark:hover:border-indigo-700">
              <f.icon className="text-indigo-500" size={22} />
              <h3 className="mt-4 font-semibold text-slate-900 dark:text-white">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{f.desc}</p>
            </Card>
          ))}
        </div>
      </Section>

      {/* How it works */}
      <Section id="how" title="How it works" subtle>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => (
            <Card key={s.title} className="p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-sm font-semibold text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-300">
                  {i + 1}
                </span>
                <s.icon size={18} className="text-slate-400" />
              </div>
              <h3 className="mt-4 font-semibold text-slate-900 dark:text-white">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{s.desc}</p>
            </Card>
          ))}
        </div>
      </Section>

      {/* Inputs / Outputs */}
      <Section id="io" title="Supported inputs & outputs">
        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">Inputs</h3>
            <div className="space-y-3">
              {INPUTS.map((i) => (
                <Card key={i.title} className="flex items-center gap-4 p-4">
                  <i.icon className="text-indigo-500" size={20} />
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">{i.title}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{i.desc}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">Outputs</h3>
            <div className="grid grid-cols-2 gap-3">
              {OUTPUTS.map((o) => (
                <Card key={o.title} className="flex items-center gap-3 p-4">
                  <o.icon className="text-emerald-500" size={20} />
                  <p className="font-medium text-slate-900 dark:text-white">{o.title}</p>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* Architecture */}
      <Section id="architecture" title="Architecture" subtle>
        <Card className="p-8">
          <div className="flex flex-col items-stretch gap-4 md:flex-row md:items-center md:justify-between">
            {[
              { icon: Boxes, label: "Next.js", sub: "Vercel" },
              { icon: TerminalSquare, label: "FastAPI", sub: "Render" },
              { icon: Sparkles, label: "Groq LLM", sub: "Test gen" },
              { icon: Gauge, label: "PostgreSQL", sub: "Supabase" },
            ].map((node, i, arr) => (
              <div key={node.label} className="flex flex-1 items-center gap-4">
                <div className="flex flex-1 flex-col items-center rounded-lg border border-slate-200 bg-slate-50 p-4 text-center dark:border-slate-800 dark:bg-slate-900">
                  <node.icon className="text-indigo-500" size={22} />
                  <p className="mt-2 font-medium text-slate-900 dark:text-white">{node.label}</p>
                  <p className="text-xs text-slate-500">{node.sub}</p>
                </div>
                {i < arr.length - 1 && (
                  <ArrowRight className="hidden shrink-0 text-slate-300 md:block dark:text-slate-700" size={18} />
                )}
              </div>
            ))}
          </div>
          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Async work runs via FastAPI BackgroundTasks — no Docker, Redis, or paid infrastructure.
          </p>
        </Card>
      </Section>

      {/* CTA */}
      <section className="px-4 py-20 sm:px-6">
        <Card className="mx-auto max-w-4xl overflow-hidden border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 p-10 text-center dark:border-indigo-900/50 dark:from-indigo-950/40 dark:to-violet-950/40">
          <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl dark:text-white">
            Ready to generate your test suite?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-slate-600 dark:text-slate-300">
            Paste a function and get comprehensive, runnable pytest tests in seconds.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <ButtonLink href="/analyze" size="lg">
              Analyze code <ArrowRight size={18} />
            </ButtonLink>
            <Link
              href="/analyze"
              className="inline-flex items-center justify-center gap-2 rounded-lg px-6 py-3 text-base font-medium text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
            >
              Upload a project
            </Link>
          </div>
        </Card>
      </section>

      <Footer />
    </div>
  );
}

function Section({
  id,
  title,
  subtle,
  children,
}: {
  id: string;
  title: string;
  subtle?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section
      id={id}
      className={subtle ? "bg-slate-50 dark:bg-slate-900/30" : undefined}
    >
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <h2 className="mb-10 text-center text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          {title}
        </h2>
        {children}
      </div>
    </section>
  );
}
