export function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-sm text-slate-500 sm:flex-row sm:px-6 dark:text-slate-400">
        <p>© {new Date().getFullYear()} TestCaseAI — AI-generated tests for your code.</p>
        <p>
          Built with FastAPI · Next.js · Groq. Deployed on Vercel + Render.
        </p>
      </div>
    </footer>
  );
}
