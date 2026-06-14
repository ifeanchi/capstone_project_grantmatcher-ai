import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Loader2, ExternalLink, Sparkles, Shield, 
  CheckCircle2, AlertCircle, ArrowUpRight, Building2, 
  Calendar, Banknote, Tag, ChevronRight 
} from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/health/ollama')
      .then(res => res.json())
      .then(data => setOllamaStatus(data))
      .catch(() => setOllamaStatus({ status: 'offline', message: 'API unreachable' }));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return setError('Please describe your project to begin.');
    
    setLoading(true);
    setError('');
    setResults([]);
    setHasSearched(true);

    try {
      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Search failed');
      setResults(data.slice(0, 3));
    } catch (err) {
      setError('Connection failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fafafa] text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* Subtle Background Mesh */}
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(99,102,241,0.15),rgba(255,255,255,0))] pointer-events-none" />

      {/* Glass Header */}
      <header className="sticky top-0 z-50 border-b border-white/60 bg-white/60 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 shadow-lg shadow-indigo-500/20">
              <Shield className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight">GrantMatcher AI</span>
          </div>
          {ollamaStatus && (
            <div className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium backdrop-blur-md ${
              ollamaStatus.status === 'ok' ? 'border-emerald-200 bg-emerald-50/80 text-emerald-700' :
              ollamaStatus.status === 'mock' ? 'border-amber-200 bg-amber-50/80 text-amber-700' :
              'border-slate-200 bg-slate-50/80 text-slate-600'
            }`}>
              {ollamaStatus.status === 'ok' ? <CheckCircle2 className="h-3 w-3" /> : <Sparkles className="h-3 w-3" />}
              {ollamaStatus.status === 'mock' ? 'Demo Mode' : ollamaStatus.status === 'ok' ? 'AI Active' : 'Offline'}
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 pb-24 pt-12">
        {/* Hero & Search */}
        <motion.div 
          initial={{ opacity: 0, y: 12 }} 
          animate={{ opacity: 1, y: 0 }} 
          className="mb-16 text-center"
        >
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            GrantMatcher AI <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">actually fits</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-slate-500">
            An intelligent grant discovery system that combines semantic search with LLM reasoning to help nonprofits and researchers find relevant funding opportunities faster.
          </p>
        </motion.div>

        {/* Floating Search Bar */}
        <motion.form 
          onSubmit={handleSearch}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative mx-auto mb-16 max-w-2xl"
        >
          <div className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-shadow hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your initiative, target audience, and goals..."
              className="min-h-[120px] w-full resize-none border-0 bg-transparent p-6 text-base leading-relaxed text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-0"
              disabled={loading}
            />
            <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50/50 px-4 py-3">
              <span className="text-xs text-slate-400">Returns exactly 3 curated matches</span>
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-slate-900/10 transition-all hover:bg-indigo-600 hover:shadow-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                {loading ? 'Analyzing...' : 'Search'}
              </button>
            </div>
          </div>
        </motion.form>

        {/* Error State */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mx-auto mb-10 flex max-w-2xl items-center gap-3 rounded-xl border border-red-200 bg-red-50/80 p-4 text-sm text-red-700 backdrop-blur-sm"
            >
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mx-auto flex max-w-2xl flex-col items-center py-16 text-center"
          >
            <div className="relative mb-4 flex h-12 w-12 items-center justify-center">
              <div className="absolute inset-0 animate-ping rounded-full bg-indigo-100 opacity-75" />
              <Loader2 className="relative h-6 w-6 animate-spin text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold">Evaluating opportunities</h3>
            <p className="mt-1 text-sm text-slate-500">Running semantic matching + AI rationale generation</p>
          </motion.div>
        )}

        {/* Results */}
        <AnimatePresence mode="wait">
          {!loading && results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-5"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold tracking-tight">Top Matches</h2>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-500">
                  {results.length} result{results.length !== 1 ? 's' : ''}
                </span>
              </div>

              {results.map((grant, i) => (
                <motion.article
                  key={grant.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-indigo-200 hover:shadow-md"
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
                    <div className="flex-1">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
                          grant.relevance_score >= 90 ? 'border-emerald-200 bg-emerald-50 text-emerald-700' :
                          grant.relevance_score >= 75 ? 'border-indigo-200 bg-indigo-50 text-indigo-700' :
                          'border-slate-200 bg-slate-50 text-slate-600'
                        }`}>
                          {grant.relevance_score}% match
                        </span>
                        {grant._source === 'mock' && (
                          <span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                            Demo
                          </span>
                        )}
                      </div>
                      <h3 className="text-xl font-semibold tracking-tight group-hover:text-indigo-600 transition-colors">
                        {grant.title}
                      </h3>
                      <div className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                        <Building2 className="h-4 w-4" />
                        {grant.organization}
                      </div>
                    </div>
                    <a
                      href={grant.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-all hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 sm:mt-1"
                    >
                      <div className="flex items-center gap-1.5">
                        View Details <ArrowUpRight className="h-4 w-4" />
                      </div>
                    </a>
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-3">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-slate-400">
                        <Calendar className="h-3.5 w-3.5" /> Deadline
                      </div>
                      <p className="text-sm font-semibold">{grant.deadline || 'Rolling'}</p>
                    </div>
                    <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-3">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-slate-400">
                        <Banknote className="h-3.5 w-3.5" /> Funding
                      </div>
                      <p className="text-sm font-semibold">${grant.min_amount?.toLocaleString()}–{grant.max_amount?.toLocaleString()}</p>
                    </div>
                    <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-3 col-span-2 sm:col-span-2">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-slate-400">
                        <Tag className="h-3.5 w-3.5" /> Field
                      </div>
                      <p className="text-sm font-semibold">{grant.field}</p>
                    </div>
                  </div>

                  <div className="mt-4 rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50/50 to-violet-50/50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-indigo-900">
                      <Sparkles className="h-3.5 w-3.5" /> AI Rationale
                    </div>
                    <p className="text-sm leading-relaxed text-indigo-900/80 italic">
                      "{grant.rationale}"
                    </p>
                  </div>
                </motion.article>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!loading && hasSearched && results.length === 0 && !error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center py-16 text-center"
          >
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <Search className="h-6 w-6 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold">No matches found</h3>
            <p className="mt-1 max-w-sm text-sm text-slate-500">
              Try broadening your description or removing niche keywords to surface more opportunities.
            </p>
          </motion.div>
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="mx-auto max-w-6xl px-6 py-8 text-center">
          <p className="text-xs text-slate-500">
            AI suggestions are advisory. Always verify eligibility directly with funders.
            <span className="mx-1 opacity-50">•</span>
            Local inference via Ollama
            <span className="mx-1 opacity-50">•</span>
            No external data sharing
          </p>
        </div>
      </footer>
    </div>
  );
}