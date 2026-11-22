import React from 'react'

/**
 * HighlightStudio – shows generated highlights video and download controls.
 * Props:
 *   result – object returned from backend (contains .highlights path)
 *   jsonData – full submission JSON (may contain highlights info)
 */
export default function HighlightStudio({ result, jsonData }) {
  if (!result || !result.highlights) return null

  const highlightsPath = `/${result.highlights.replace('./', '')}`
  const highlightDuration = (jsonData?.highlights || []).reduce(
    (sum, h) => sum + (h.segment ? h.segment[1] - h.segment[0] : 0),
    0
  )
  const originalDuration = jsonData?.duration_sec ?? 0
  const compression = originalDuration
    ? ((originalDuration - highlightDuration) / originalDuration) * 100
    : 0

  return (
    <section className="mt-8">
      <h3 className="text-2xl font-semibold text-secondary mb-3">Highlight Studio</h3>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <p className="text-muted mb-1">Generated Highlights</p>
          <video src={highlightsPath} controls className="w-full rounded" />
        </div>
        <div className="flex flex-col space-y-2">
          <button
            onClick={() => {
              const link = document.createElement('a')
              link.href = highlightsPath
              link.download = 'highlights.mp4'
              document.body.appendChild(link)
              link.click()
              link.remove()
            }}
            className="neon-border flex items-center space-x-2 px-3 py-1 rounded"
          >
            Download MP4
          </button>
          <p>Original Duration: {originalDuration.toFixed(2)}s</p>
          <p>Highlight Duration: {highlightDuration.toFixed(2)}s</p>
          <p>Compression: {compression.toFixed(1)}% saved</p>
        </div>
      </div>
    </section>
  )
}
