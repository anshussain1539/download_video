import { useState } from 'react'
import './App.css'

function parseFilename(disposition) {
  if (!disposition) return null
  const utf8 = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8) {
    try { return decodeURIComponent(utf8[1]) } catch { /* fall through */ }
  }
  const plain = disposition.match(/filename="?([^";]+)"?/i)
  return plain ? plain[1] : null
}

export default function App() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    setStatus('downloading')
    setError('')
    try {
      const res = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: trimmed }),
      })
      if (!res.ok) {
        let msg = `Request failed (${res.status})`
        try {
          const data = await res.json()
          if (data?.detail) msg = data.detail
        } catch { /* keep default */ }
        throw new Error(msg)
      }

      const filename = parseFilename(res.headers.get('Content-Disposition')) || 'video.mp4'
      const blob = await res.blob()
      const objectUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = objectUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(objectUrl)
      setStatus('done')
    } catch (err) {
      setError(err.message || 'Download failed')
      setStatus('error')
    }
  }

  return (
    <div className="container">
      <h1>Video Downloader</h1>
      <p className="subtitle">
        Paste a TikTok, YouTube, Instagram, Facebook, or other video link.
      </p>

      <form onSubmit={onSubmit}>
        <input
          type="url"
          placeholder="https://..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={status === 'downloading'}
          required
        />
        <button type="submit" disabled={status === 'downloading' || !url.trim()}>
          {status === 'downloading' ? 'Downloading…' : 'Download'}
        </button>
      </form>

      {status === 'downloading' && (
        <p className="hint">Fetching video from source… this can take a moment.</p>
      )}
      {status === 'done' && <p className="success">Saved to your downloads folder.</p>}
      {status === 'error' && <p className="error">{error}</p>}
    </div>
  )
}
