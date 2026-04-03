import { useState, useEffect, useRef } from 'react'
import './index.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const STATUS_STEPS = [
  'Fetching conversation...',
  'Parsing messages...',
  'Analyzing content...',
  'Generating snapshot...',
  'Almost done...',
]

function useStatusCycle(active) {
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    if (!active) {
      setStepIndex(0)
      return
    }
    const interval = setInterval(() => {
      setStepIndex(i => (i + 1 < STATUS_STEPS.length ? i + 1 : i))
    }, 3500)
    return () => clearInterval(interval)
  }, [active])

  return STATUS_STEPS[stepIndex]
}

function Navbar() {
  return (
    <nav className="border-b border-border">
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <span className="font-semibold text-white tracking-tight">ContextSync</span>
        <span className="text-muted text-xs hidden sm:block">AI memory for long-running projects</span>
      </div>
    </nav>
  )
}

function PulsingDots() {
  return (
    <span className="flex items-center gap-1">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-accent"
          style={{ animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite` }}
        />
      ))}
    </span>
  )
}

function ProcessingState({ statusMessage }) {
  return (
    <div className="flex items-center gap-3 h-[52px] px-4 animate-fade-in">
      <PulsingDots />
      <span key={statusMessage} className="text-muted text-sm animate-fade-in">
        {statusMessage}
      </span>
    </div>
  )
}

function ResultArea({ snapshot, onReset }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(snapshot).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="mt-10 animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
          Context Snapshot
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className={`h-8 px-4 rounded-md text-xs font-medium transition-all duration-200 border
              ${copied
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10'
                : 'border-border text-muted hover:text-white hover:border-white/20'
              }`}
          >
            {copied ? 'Copied!' : 'Copy to clipboard'}
          </button>
          <button onClick={onReset} className="btn-ghost text-xs h-8 px-4">
            Start over
          </button>
        </div>
      </div>
      <textarea
        readOnly
        value={snapshot}
        className="w-full min-h-[420px] p-5 rounded-lg bg-surface border border-border
                   text-sm text-white/80 font-mono leading-relaxed
                   resize-y scrollbar-thin focus:outline-none focus:border-accent/40"
        style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}
      />
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="mt-4 flex items-start gap-3 p-4 rounded-lg border border-red-500/30 bg-red-500/5 animate-fade-in">
      <span className="text-red-400 text-xs mt-0.5">✕</span>
      <div className="flex-1 min-w-0">
        <p className="text-red-400 text-sm font-medium">Extraction failed</p>
        <p className="text-muted text-xs mt-1 break-words">{message}</p>
      </div>
      <button onClick={onRetry} className="btn-ghost text-xs h-8 px-4 shrink-0">
        Try again
      </button>
    </div>
  )
}

export default function App() {
  const [url, setUrl] = useState('')
  const [jobId, setJobId] = useState(null)
  const [phase, setPhase] = useState('idle') // idle | loading | done | error
  const [snapshot, setSnapshot] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const pollRef = useRef(null)

  const statusMessage = useStatusCycle(phase === 'loading')

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  const reset = () => {
    stopPolling()
    setJobId(null)
    setPhase('idle')
    setSnapshot('')
    setErrorMsg('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim() || phase === 'loading') return

    reset()
    setPhase('loading')

    try {
      const res = await fetch(`${API_URL}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Server error ${res.status}`)
      }

      const { job_id } = await res.json()
      setJobId(job_id)
    } catch (err) {
      setPhase('error')
      setErrorMsg(err.message)
    }
  }

  useEffect(() => {
    if (!jobId || phase !== 'loading') return

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/status/${jobId}`)
        if (!res.ok) return
        const data = await res.json()

        if (data.status === 'done') {
          stopPolling()
          setSnapshot(data.result || '')
          setPhase('done')
        } else if (data.status === 'error') {
          stopPolling()
          setErrorMsg(data.error || 'Unknown error')
          setPhase('error')
        }
      } catch {
        // network blip — keep polling
      }
    }, 3000)

    return stopPolling
  }, [jobId, phase])

  const isLoading = phase === 'loading'
  const isDone = phase === 'done'
  const isError = phase === 'error'

  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <Navbar />

      {/* Hero */}
      <main className="flex-1">
        <section className="relative py-24 px-6 overflow-hidden">
          {/* Radial glow */}
          <div
            className="pointer-events-none absolute inset-0 flex items-start justify-center"
            aria-hidden="true"
          >
            <div
              className="w-[700px] h-[400px] rounded-full"
              style={{
                background: 'radial-gradient(ellipse at center, rgba(99,102,241,0.05) 0%, transparent 70%)',
                transform: 'translateY(-30%)',
              }}
            />
          </div>

          <div className="relative max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 rounded-full border border-border bg-surface text-xs text-muted">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              AI context extraction — instant, private, local
            </div>

            <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.08] mb-5">
              Never lose context<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-indigo-400">
                between AI sessions
              </span>
            </h1>

            <p className="text-muted text-lg leading-relaxed max-w-xl mx-auto mb-12">
              Paste a ChatGPT share link and get a ready-to-paste context snapshot
              in seconds — so your next session picks up exactly where you left off.
            </p>

            {/* Input form */}
            <form
              onSubmit={handleSubmit}
              className="flex flex-col sm:flex-row gap-3 max-w-2xl mx-auto"
            >
              <input
                type="url"
                className="input-field flex-1"
                placeholder="https://chatgpt.com/share/..."
                value={url}
                onChange={e => setUrl(e.target.value)}
                disabled={isLoading}
                required
              />
              {!isLoading && (
                <button type="submit" className="btn-primary" disabled={!url.trim()}>
                  Extract Context
                </button>
              )}
            </form>

            {/* Processing indicator */}
            {isLoading && (
              <div className="mt-4 flex justify-center">
                <ProcessingState statusMessage={statusMessage} />
              </div>
            )}

            {/* Error state */}
            {isError && (
              <div className="max-w-2xl mx-auto mt-2">
                <ErrorState message={errorMsg} onRetry={reset} />
              </div>
            )}
          </div>
        </section>

        {/* Result */}
        {isDone && (
          <section className="px-6 pb-24">
            <div className="max-w-3xl mx-auto">
              <ResultArea snapshot={snapshot} onReset={reset} />
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-border py-6 px-6">
        <div className="max-w-5xl mx-auto text-center text-muted text-xs">
          © {new Date().getFullYear()} ContextSync. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
