import React, { useEffect, useState } from 'react'

/**
 * ActionTimeline – a lightweight timeline visualiser.
 * Props:
 *   actions: [{ verb, noun, start, end, confidence }]
 *   videoDuration: number (seconds)
 *   videoRef: React ref to the main video element
 */
export default function ActionTimeline({ actions = [], videoDuration = 0, videoRef }) {
  const [currentTime, setCurrentTime] = useState(0)

  // Sync with video playback
  useEffect(() => {
    const video = videoRef?.current
    if (!video) return
    const handler = () => setCurrentTime(video.currentTime)
    video.addEventListener('timeupdate', handler)
    return () => video.removeEventListener('timeupdate', handler)
  }, [videoRef])

  const toPercent = (t) => (videoDuration ? (t / videoDuration) * 100 : 0)

  // Arrange actions into non‑overlapping lanes for visual stacking
  const lanes = []
  actions
    .slice()
    .sort((a, b) => a.start - b.start)
    .forEach((a) => {
      let placed = false
      for (const lane of lanes) {
        const last = lane[lane.length - 1]
        if (a.start >= last.end) {
          lane.push(a)
          placed = true
          break
        }
      }
      if (!placed) lanes.push([a])
    })

  const laneHeight = 20
  const containerHeight = Math.max(lanes.length, 1) * laneHeight + 20

  const handleClick = (t) => {
    if (videoRef?.current) videoRef.current.currentTime = t
  }

  return (
    <div className="mt-4">
      <h3 className="text-2xl font-semibold text-secondary mb-2">Action Timeline</h3>
      <div className="relative w-full border border-surface/30 rounded" style={{ height: `${containerHeight}px` }}>
        {/* Ruler marks */}
        <div className="absolute inset-0 flex" style={{ height: '100%' }}>
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="border-r border-surface/20"
              style={{ left: `${(i / 4) * 100}%`, width: 0, position: 'absolute' }}
            >
              <span className="text-xs text-muted" style={{ position: 'absolute', top: '-1.2rem', left: '-0.5rem' }}>
                {(videoDuration * (i / 4)).toFixed(1)}s
              </span>
            </div>
          ))}
        </div>
        {/* Action blocks */}
        {lanes.map((lane, laneIdx) => (
          <React.Fragment key={laneIdx}>
            {lane.map((a, idx) => {
              const left = toPercent(a.start)
              const width = toPercent(a.end - a.start)
              const isCurrent = currentTime >= a.start && currentTime <= a.end
              const label = `${a.verb} ${a.noun}`.trim()
              return (
                <div
                  key={idx}
                  className={`absolute rounded cursor-pointer transition-all ${isCurrent ? 'bg-primary' : 'bg-primary/40'} hover:bg-primary/70`}
                  style={{
                    left: `${left}%`,
                    width: `${width}%`,
                    top: `${laneIdx * laneHeight + 5}px`,
                    height: `${laneHeight - 4}px`,
                  }}
                  title={`${label}\n${a.start.toFixed(2)}s – ${a.end.toFixed(2)}s\nConfidence: ${(a.confidence * 100).toFixed(1)}%`}
                  onClick={() => handleClick(a.start)}
                />
              )
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
