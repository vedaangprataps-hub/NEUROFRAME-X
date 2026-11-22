import React from 'react'

/**
 * ActionAnalytics – display simple statistics derived from the JSON result.
 * Props:
 *   jsonData – the full submission JSON (or null)
 */
export default function ActionAnalytics({ jsonData }) {
  if (!jsonData) return null

  const actions = jsonData.actions || []
  const total = actions.length
  const avgConfidence =
    total > 0
      ? actions.reduce((sum, a) => sum + (a.score ?? a.confidence ?? 0), 0) / total
      : 0

  const duration = jsonData.duration_sec ?? 0
  const highlightDur = (jsonData.highlights || []).reduce(
    (sum, h) => sum + (h.segment ? h.segment[1] - h.segment[0] : 0),
    0
  )
  const highlightPct = duration ? (highlightDur / duration) * 100 : 0

  return (
    <section className="mt-8">
      <h3 className="text-2xl font-semibold text-secondary mb-3">Analytics</h3>
      <ul className="list-disc pl-5 text-text">
        <li>Total actions detected: {total}</li>
        <li>Average confidence: {(avgConfidence * 100).toFixed(1)}%</li>
        <li>Video duration: {duration.toFixed(2)} s</li>
        <li>Highlight duration: {highlightDur.toFixed(2)} s ({highlightPct.toFixed(1)}% of video)</li>
      </ul>
    </section>
  )
}
