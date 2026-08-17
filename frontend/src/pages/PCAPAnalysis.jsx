import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import {
  Upload, Play, CheckCircle2, Circle, Loader2,
  FileSearch, Wifi, Shield, AlertTriangle, Globe, Info
} from 'lucide-react';

import { uploadPCAP } from '../api/apiService.js';
import { mockPCAPResult } from '../mock/mockData.js';
import usePageMeta from '../hooks/usePageMeta.js';
import RiskBadge  from '../components/common/RiskBadge.jsx';
import FileUpload from '../components/common/FileUpload.jsx';

// ── Processing stages ───────────────────────────────────────
const STAGES = [
  { id: 'upload',   label: 'File Received',            icon: Upload },
  { id: 'parse',    label: 'Parsing PCAP packets',     icon: FileSearch },
  { id: 'extract',  label: 'Extracting HTTP requests', icon: Wifi },
  { id: 'ml',       label: 'Running ML classifier',    icon: Shield },
  { id: 'complete', label: 'Analysis Complete',         icon: CheckCircle2 },
];

const STAGE_DELAYS = [600, 800, 900, 1000, 400];

// ── Processing Step ─────────────────────────────────────────
function ProcessingStep({ stage, status }) {
  const { label, icon: Icon } = stage;
  return (
    <div className="flex items-center gap-4">
      <div className={`step-icon ${status}`}>
        {status === 'active' ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : status === 'done' ? (
          <CheckCircle2 className="w-4 h-4" />
        ) : (
          <Circle className="w-4 h-4" />
        )}
      </div>
      <span className="text-sm font-medium"
            style={{
              color: status === 'done' ? '#F3E8BC' : status === 'active' ? 'var(--text-primary)' : 'var(--text-muted)'
            }}>
        {label}
      </span>
      {status === 'active' && (
        <span className="text-xs font-mono animate-pulse" style={{ color: 'var(--text-muted)' }}>
          processing...
        </span>
      )}
    </div>
  );
}

// ── Result Stat Card ─────────────────────────────────────────
function ResultCard({ icon: Icon, label, value, accentColor = '#035352' }) {
  return (
    <div className="glass-card-hover p-4 flex items-center gap-4"
         style={{ border: `1px solid ${accentColor}30` }}>
      <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
           style={{ background: `${accentColor}18` }}>
        <Icon className="w-5 h-5" style={{ color: accentColor }} />
      </div>
      <div>
        <p className="text-xs uppercase tracking-wider mb-0.5" style={{ color: 'var(--text-muted)' }}>{label}</p>
        <p className="text-2xl font-bold num-display" style={{ color: '#F3E8BC' }}>{value?.toLocaleString()}</p>
      </div>
    </div>
  );
}

export default function PCAPAnalysis() {
  usePageMeta('PCAP Analysis', 'NetTrace Security — Upload PCAP files for automated HTTP extraction and cyberattack detection.');
  const [file, setFile]             = useState(null);
  const [processing, setProcessing] = useState(false);
  const [stageIdx, setStageIdx]     = useState(-1);
  const [result, setResult]         = useState(null);
  const [error, setError]           = useState('');

  const runAnalysis = async (pcapFile) => {
    setProcessing(true);
    setResult(null);
    setError('');
    setStageIdx(0);

    for (let i = 0; i < STAGES.length - 1; i++) {
      setStageIdx(i);
      await new Promise(r => setTimeout(r, STAGE_DELAYS[i]));
    }

    try {
      const data = await uploadPCAP(pcapFile);
      setStageIdx(STAGES.length - 1);
      await new Promise(r => setTimeout(r, 500));
      setResult(data);
    } catch (err) {
      setError('Analysis failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const loadDemo = () => {
    const fake = new File(['demo'], 'demo_capture.pcap', { type: 'application/octet-stream' });
    setFile(fake);
    runAnalysis(fake);
  };

  return (
    <div className="space-y-5 animate-fade-in">

      {/* ── Notice ────────────────────────────────────── */}
      <div className="flex items-center gap-2 text-xs rounded-lg px-4 py-2.5"
           style={{ background: 'rgba(243,232,188,0.05)', border: '1px solid rgba(243,232,188,0.12)' }}>
        <Info className="w-4 h-4 flex-shrink-0" style={{ color: '#F3E8BC' }} />
        <span style={{ color: 'var(--text-muted)' }}>
          Demo mode: Uploading any PCAP file triggers <strong style={{ color: '#F3E8BC' }}>simulated analysis</strong> with synthetic results. No real packet data is processed.
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* ── Upload panel ──────────────────────────── */}
        <div className="glass-card p-5 space-y-4">
          <h2 className="text-sm font-semibold flex items-center gap-2" style={{ color: '#F3E8BC' }}>
            <Upload className="w-4 h-4" />
            Upload PCAP File
          </h2>

          <FileUpload
            onFile={(f) => { setFile(f); }}
            accept=".pcap,.cap,.pcapng"
            label="Drop PCAP file here"
            hint="Supports .pcap, .cap, .pcapng formats"
          />

          <div className="flex gap-3">
            <button
              onClick={() => file && runAnalysis(file)}
              disabled={!file || processing}
              className="btn-primary flex-1 justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {processing ? 'Analysing...' : 'Analyse PCAP'}
            </button>
            <button
              onClick={loadDemo}
              disabled={processing}
              className="btn-secondary disabled:opacity-50"
            >
              <FileSearch className="w-4 h-4" />
              Load Demo
            </button>
          </div>

          {/* File info */}
          {file && (
            <div className="rounded-xl px-4 py-3 flex items-center gap-3"
                 style={{ background: 'rgba(3,83,82,0.10)', border: '1px solid rgba(3,83,82,0.22)' }}>
              <FileSearch className="w-4 h-4 flex-shrink-0" style={{ color: '#F3E8BC' }} />
              <div className="min-w-0">
                <p className="text-xs font-medium truncate" style={{ color: '#F3E8BC' }}>{file.name}</p>
                <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                  {file.size > 0 ? `${(file.size / 1024).toFixed(1)} KB` : 'Demo file'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* ── Processing pipeline ───────────────────── */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold mb-6 flex items-center gap-2" style={{ color: '#F3E8BC' }}>
            <Shield className="w-4 h-4" />
            Processing Pipeline
          </h2>
          <div className="space-y-5">
            {STAGES.map((stage, i) => {
              const status = i < stageIdx ? 'done' : i === stageIdx ? 'active' : 'pending';
              return <ProcessingStep key={stage.id} stage={stage} status={status} />;
            })}
          </div>

          {stageIdx === STAGES.length - 1 && !processing && result && (
            <div className="mt-5 flex items-center gap-2 text-xs rounded-lg p-3"
                 style={{ background: 'rgba(3,83,82,0.12)', border: '1px solid rgba(3,83,82,0.30)' }}>
              <CheckCircle2 className="w-4 h-4" style={{ color: '#F3E8BC' }} />
              <span style={{ color: '#F3E8BC' }}>
                Analysis complete — {result.processing_time_ms}ms processing time
              </span>
            </div>
          )}

          {error && (
            <div className="mt-5 flex items-center gap-2 text-xs rounded-lg p-3"
                 style={{ background: 'rgba(180,30,30,0.10)', border: '1px solid rgba(180,30,30,0.25)' }}>
              <AlertTriangle className="w-4 h-4" style={{ color: '#f87171' }} />
              <span style={{ color: '#f87171' }}>{error}</span>
            </div>
          )}

          {stageIdx === -1 && (
            <p className="text-xs font-mono text-center mt-6" style={{ color: 'var(--text-muted)' }}>
              Upload a PCAP or click "Load Demo" to begin
            </p>
          )}
        </div>
      </div>

      {/* ── Results ────────────────────────────────────── */}
      {result && (
        <div className="space-y-5 animate-fade-in">
          {/* Summary cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <ResultCard icon={FileSearch} label="Packets Processed" value={result.packets_processed} accentColor="#035352" />
            <ResultCard icon={Wifi}       label="HTTP Requests"     value={result.http_requests_extracted} accentColor="#04817f" />
            <ResultCard icon={Shield}     label="Attacks Detected"  value={result.attacks_detected} accentColor="#f87171" />
            <ResultCard icon={Globe}      label="High-Risk IPs"     value={result.high_risk_ips} accentColor="#fb923c" />
          </div>

          {/* Detected attacks table */}
          <div className="glass-card overflow-hidden">
            <div className="section-header">
              <h3 className="section-title flex items-center gap-2">
                <Shield className="w-4 h-4" style={{ color: '#F3E8BC' }} />
                Detected Attacks
                <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>({result.attacks.length})</span>
              </h3>
              <span className="chip" style={{ color: '#F3E8BC', borderColor: 'rgba(243,232,188,0.2)' }}>SIMULATED</span>
            </div>
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Source IP</th>
                    <th>Attack Type</th>
                    <th>Severity</th>
                    <th>Confidence</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {result.attacks.slice(0, 15).map(atk => (
                    <tr key={atk.id}>
                      <td className="font-mono text-xs whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                        {format(parseISO(atk.timestamp), 'MM/dd HH:mm:ss')}
                      </td>
                      <td className="font-mono text-xs whitespace-nowrap" style={{ color: '#F3E8BC' }}>
                        {atk.source_ip}
                      </td>
                      <td style={{ color: 'var(--text-primary)' }}>{atk.attack_type}</td>
                      <td><RiskBadge severity={atk.severity} /></td>
                      <td>
                        <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                          {(atk.confidence * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td>
                        <span className="text-xs font-mono font-semibold"
                              style={{ color: atk.result === 'POTENTIAL_SUCCESS' ? '#f87171' : '#fbbf24' }}>
                          {atk.result === 'POTENTIAL_SUCCESS' ? '⚡ SUCCESS' : '⚠ ATTEMPT'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
