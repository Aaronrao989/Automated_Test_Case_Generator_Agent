/**
 * Minimal, dependency-free Python syntax highlighter.
 * Escapes HTML first, then wraps tokens in <span class="tok-*">.
 * Good enough for read-only display of generated tests.
 */

const KEYWORDS = new Set([
  "def", "return", "import", "from", "as", "class", "if", "elif", "else",
  "for", "while", "in", "not", "and", "or", "is", "None", "True", "False",
  "with", "try", "except", "finally", "raise", "assert", "pass", "lambda",
  "yield", "global", "nonlocal", "del", "await", "async",
]);

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function highlightPython(code: string): string {
  const escaped = escapeHtml(code);
  // Order matters: comments and strings first so keywords inside them are skipped.
  const pattern =
    /(#.*?$)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d+\.?\d*\b)|(@\w+)|(\bdef\s+)(\w+)|(\b\w+\b)/gm;

  return escaped.replace(
    pattern,
    (match, comment, str, num, decorator, defKw, defName, word) => {
      if (comment) return `<span class="tok-com">${comment}</span>`;
      if (str) return `<span class="tok-str">${str}</span>`;
      if (num) return `<span class="tok-num">${num}</span>`;
      if (decorator) return `<span class="tok-dec">${decorator}</span>`;
      if (defKw) return `<span class="tok-kw">${defKw}</span><span class="tok-fn">${defName}</span>`;
      if (word) {
        if (KEYWORDS.has(word)) return `<span class="tok-kw">${word}</span>`;
        return word;
      }
      return match;
    }
  );
}
