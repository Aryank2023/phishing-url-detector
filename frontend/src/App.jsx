import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

const initialResult = {
  result: "",
  confidence: null,
  normalized_url: "",
};

function isValidInput(value) {
  const candidate = value.trim();
  if (!candidate) return false;

  try {
    const normalized = /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(candidate)
      ? candidate
      : `https://${candidate}`;
    const parsed = new URL(normalized);
    return Boolean(parsed.hostname && parsed.hostname.includes("."));
  } catch {
    return false;
  }
}

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(initialResult);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(initialResult);

    if (!isValidInput(url)) {
      setError("Enter a valid URL like example.com or https://example.com.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Prediction failed.");
      }

      setResult(payload);
    } catch (requestError) {
      setError(requestError.message || "Unable to reach the prediction service.");
    } finally {
      setLoading(false);
    }
  };

  const hasResult = Boolean(result.result);
  const isPhishing = result.result === "phishing";

  return (
    <main className="relative overflow-hidden px-6 py-10 text-mist sm:px-10 lg:px-16">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[-7rem] top-14 h-56 w-56 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute right-[-5rem] top-20 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute bottom-[-4rem] left-1/3 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl" />
      </div>

      <section className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-6xl flex-col justify-center gap-12 lg:flex-row lg:items-center">
        <div className="max-w-2xl animate-rise">
          <span className="inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm tracking-[0.24em] text-sky-100/80 uppercase">
            ML-Powered Threat Screening
          </span>
          <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-tight text-white sm:text-6xl">
            Detect malicious URLs before they reach your users.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-200/80">
            PhishGuard analyzes suspicious URL patterns and predicts whether a link is
            safe or phishing in seconds, with confidence scoring and input validation
            built in.
          </p>

          <div className="mt-8 flex flex-wrap gap-3 text-sm text-slate-100/80">
            <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-4 py-2">
              Real-time scoring
            </span>
            <span className="rounded-full border border-sky-300/20 bg-sky-300/10 px-4 py-2">
              Secure backend API
            </span>
            <span className="rounded-full border border-orange-300/20 bg-orange-300/10 px-4 py-2">
              Deployment-ready
            </span>
          </div>
        </div>

        <div className="glass-card w-full max-w-xl rounded-[2rem] border border-white/15 p-6 shadow-glow sm:p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="url-input" className="mb-3 block text-sm font-medium text-slate-100">
                Enter a URL to inspect
              </label>
              <input
                id="url-input"
                type="text"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="example.com/login"
                className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-5 py-4 text-base text-white outline-none transition focus:border-sky-400/70 focus:ring-2 focus:ring-sky-400/20"
                autoComplete="off"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center rounded-2xl bg-gradient-to-r from-sky-500 via-blue-500 to-cyan-400 px-5 py-4 text-base font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Analyzing URL..." : "Scan URL"}
            </button>
          </form>

          {loading && (
            <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/40 p-5 animate-rise">
              <div className="flex items-center gap-4">
                <div className="flex gap-2">
                  <span className="h-3 w-3 animate-pulseSoft rounded-full bg-cyan-300" />
                  <span className="h-3 w-3 animate-pulseSoft rounded-full bg-sky-400 [animation-delay:150ms]" />
                  <span className="h-3 w-3 animate-pulseSoft rounded-full bg-blue-400 [animation-delay:300ms]" />
                </div>
                <p className="text-sm text-slate-200/85">
                  Running feature extraction and model prediction...
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-2xl border border-orange-300/25 bg-orange-400/10 p-4 text-sm text-orange-100 animate-rise">
              {error}
            </div>
          )}

          {hasResult && (
            <article
              className={`mt-6 rounded-[1.75rem] border p-6 animate-rise ${
                isPhishing
                  ? "border-orange-300/25 bg-orange-500/10"
                  : "border-emerald-300/25 bg-emerald-500/10"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-slate-100/70">
                    Prediction Result
                  </p>
                  <h2 className="mt-2 text-3xl font-semibold text-white">
                    {isPhishing ? "Likely Phishing" : "Looks Safe"}
                  </h2>
                </div>
                <div
                  className={`rounded-full px-4 py-2 text-sm font-medium ${
                    isPhishing
                      ? "bg-orange-300/20 text-orange-100"
                      : "bg-emerald-300/20 text-emerald-100"
                  }`}
                >
                  {isPhishing ? "Phishing" : "Safe"}
                </div>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-950/35 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-300/70">
                    Confidence
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-white">
                    {result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : "N/A"}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/35 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-300/70">
                    Checked URL
                  </p>
                  <p className="mt-2 break-all text-sm text-slate-100/90">
                    {result.normalized_url}
                  </p>
                </div>
              </div>
            </article>
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
