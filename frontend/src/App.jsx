import { useState, useRef } from 'react';
import ActionTimeline from './components/timeline/ActionTimeline.jsx'
import ActionAnalytics from './components/ActionAnalytics.jsx'
import HighlightStudio from './components/HighlightStudio.jsx'

import { uploadVideo } from './services/api'
import axios from 'axios'
import { motion } from 'framer-motion'
import { Upload, Download, Loader2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'

const COLORS = ['#00E5FF', '#9D4EDD', '#00FFB2', '#8892A6']

export default function App() {
  const [step, setStep] = useState('IDLE') // IDLE, UPLOADING, PROCESSING, COMPLETED, FAILED
  const [file, setFile] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [result, setResult] = useState(null)
  const [jsonData, setJsonData] = useState(null)
  const [error, setError] = useState(null)
  const videoRef = useRef(null)
  const highlightRef = useRef(null)

  const handleFile = (e) => {
    const selected = e.target.files[0]
    if (selected && selected.type === 'video/mp4') {
      setFile(selected)
      setVideoUrl(URL.createObjectURL(selected))
    } else {
      setError('Please select a valid MP4 video')
    }
  }

  const startAnalysis = async () => {
    if (!file) return
    setStep('UPLOADING')
    setError(null)
    try {
      const data = await uploadVideo(file, (progressEvent) => {
        // Could hook to progress if needed
      })
      setStep('PROCESSING')
      // data.json is path like "./outputs/filename.json"
      const jsonPath = data.json.replace('./', '')
      const jsonResp = await axios.get(`/${jsonPath}`)
      setJsonData(jsonResp.data)
      setResult(data)
      setStep('COMPLETED')
    } catch (err) {
      console.error(err)
      setError('Processing failed')
      setStep('FAILED')
    }
  }

  const downloadFile = (url, name) => {
    const link = document.createElement('a')
    link.href = url
    link.download = name
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  // Compute analytics from jsonData
  const actionCounts = jsonData?.actions?.reduce((acc, a) => {
    const key = a.verb ? `${a.verb} ${a.noun}`.trim() : a.label
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {}) || {}
  const chartData = Object.entries(actionCounts).map(([k, v]) => ({ name: k, value: v }))

  const highlightDuration = jsonData?.highlights?.reduce((sum, h) => sum + (h.end - h.start), 0) || 0
  const originalDuration = jsonData?.duration || (videoRef.current?.duration || 0)
  const compression = originalDuration ? ((originalDuration - highlightDuration) / originalDuration) * 100 : 0

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <motion.div className="glass p-6 w-full max-w-5xl" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold text-primary gradient-bg bg-clip-text text-transparent mb-2">NEUROFRAME‑X</h1>
        <h2 className="text-xl text-text mb-6">XR Intelligence Engine</h2>
        {/* Upload Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-muted mb-2">Upload MP4 video</label>
          <div className="flex items-center space-x-4">
            <input type="file" accept="video/mp4" onChange={handleFile} className="hidden" id="fileInput" />
            <label htmlFor="fileInput" className="neon-border px-4 py-2 rounded cursor-pointer flex items-center space-x-2">
              <Upload size={20} className="text-primary" />
              <span>Select File</span>
            </label>
            {file && <span className="text-success">{file.name}</span>}
          </div>
        </div>
        {/* Video preview */}
        {videoUrl && (
          <div className="mb-6">
            <video ref={videoRef} src={videoUrl} controls className="w-full rounded" />
          </div>
        )}
        {/* Action button */}
        {file && step === 'IDLE' && (
          <button onClick={startAnalysis} className="neon-border text-primary px-4 py-2 rounded hover:bg-primary/10 transition">
            Analyse Video
          </button>
        )}
        {/* Loading */}
        {step === 'UPLOADING' && (
          <div className="flex items-center space-x-2 mt-4">
            <Loader2 className="animate-spin text-primary" />
            <span className="text-text">Uploading...</span>
          </div>
        )}
        {step === 'PROCESSING' && (
          <div className="flex items-center space-x-2 mt-4">
            <Loader2 className="animate-spin text-primary" />
            <span className="text-text">Processing video...</span>
          </div>
        )}
        {error && <p className="text-red-500 mt-2">{error}</p>}
        {/* Results */}
        {step === 'COMPLETED' && jsonData && (
          <div className="mt-8 space-y-8">
            <ActionTimeline actions={jsonData.actions || []} videoDuration={jsonData.duration_sec || 0} videoRef={videoRef} />
            {/* Analytics */}
            <ActionAnalytics jsonData={jsonData} />
            {/* Highlight Studio */}
            <HighlightStudio result={result} jsonData={jsonData} />
            <section className="h-64">
              <h3 className="text-2xl font-semibold text-secondary mb-3">Action Distribution</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" width={150} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#00E5FF" />
                </BarChart>
              </ResponsiveContainer>
            </section>
            {/* Highlight Studio */}
            <section>
              <h3 className="text-2xl font-semibold text-secondary mb-3">Highlight Studio</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-muted mb-1">Original Video</p>
                  <video ref={videoRef} src={videoUrl} controls className="w-full rounded" />
                </div>
                <div>
                  <p className="text-muted mb-1">Generated Highlights</p>
                  <video ref={highlightRef} src={`/${result.highlights.replace('./', '')}`} controls className="w-full rounded" />
                </div>
              </div>
              <div className="flex space-x-4 mt-4">
                <button onClick={() => downloadFile(`/${result.highlights.replace('./', '')}`, 'highlights.mp4')} className="neon-border flex items-center space-x-2 px-3 py-1 rounded">
                  <Download size={16} className="text-success" />
                  <span>Download MP4</span>
                </button>
                <button onClick={() => downloadFile(`/${result.json.replace('./', '')}`, 'analysis.json')} className="neon-border flex items-center space-x-2 px-3 py-1 rounded">
                  <Download size={16} className="text-success" />
                  <span>Download JSON</span>
                </button>
              </div>
              <div className="mt-3 text-text">
                <p>Original Duration: {originalDuration.toFixed(2)}s</p>
                <p>Highlight Duration: {highlightDuration.toFixed(2)}s</p>
                <p>Compression: {compression.toFixed(1)}% saved</p>
              </div>
            </section>
          </div>
        )}
      </motion.div>
    </div>
  )
}
