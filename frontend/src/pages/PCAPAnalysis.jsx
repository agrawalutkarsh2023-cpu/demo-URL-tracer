import { useState, useRef } from 'react';
import { format, parseISO } from 'date-fns';
import {
  Upload, Play, CheckCircle2, Circle, Loader2,
  FileSearch, Wifi, Shield, AlertTriangle, Globe, Info
} from 'lucide-react';

import { uploadPCAP } from '../api/apiService.js';
import { mockPCAPResult } from '../mock/mockData.js';
import RiskBadge  from '../components/common/RiskBadge.jsx';
import FileUpload from '../components/common/FileUpload.jsx';

// Processing stages
const STAGES = [
  { id: 'upload',    label: 'File Received',           icon: Upload },
  { id: 'parse',     label: 'Parsing PCAP packets',    icon: FileSearch },
  { id: 'extract',   label: 'Extracting HTTP requests',icon: Wifi },
  { id: 'ml',        label: 'Running ML classifier',   icon: Shield },
  { id: 'complete',  label: 'Analysis Complete',        icon: CheckCircle2 },
];

const STAGE_DELAYS = [600, 800, 900, 1000, 400]; // ms per stage

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
      <span className={`text-sm font-medium ${
        status === 'done'   ? 'text-cyber-400' :
        status === 'active' ? 'text-white' :
        'text-slate-600'
      }`}>
        {label}
      </span>
      {status === 'active' && (
        <span className="text-xs text-slate-500 animate-pulse font-mono">processing...</span>
      )}
    </div>
  );
}

function ResultCard({ icon: Icon, label, value, color }) {
  return (
    <div className={`glass-card border p-4 flex items-center gap-4 ${color}`}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-dark-800">
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold text-white font-mono">{value?.toLocaleString()}</p>
      </div>
    </div>
  );
}

export default function PCAPAnalysis() {
  const [file, setFile]           = useState(null);
  const [processing, setProcessing] = useState(false);
  const [stageIdx, setStageIdx]   = useState(-1);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState('');

  const runAnalysis = async (pcapFile) => {
    setProcessing(true);
    setResult(null);
    setError('');
    setStageIdx(0);

    // Animate through stages
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
    // Simulate selecting a demo file
    const fake = new File(['demo'], 'demo_capture.pcap', { type: 'application/octet-stream' });
    setFile(fake);
    runAnalysis(fake);
  };

  return (
    <div className="space-y-5 animate-fade-in">

      {/* Notice */}
      <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2.5">
        <Info className="w-4 h-4 flex-shrink-0" />
        Demo mode: Uploading any PCAP file triggers <strong>simulated analysis</strong> with synthetic results.
        No real packet data is processed.
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Upload panel */}
        <div className="glass-card border border-dark-600/50 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-white">Upload PCAP File</h2>

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
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
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
        </div>

        {/* Processing stages */}
        <div className="glass-card border border-dark-600/50 p-5">
          <h2 className="text-sm font-semibold text-white mb-5">Processing Pipeline</h2>
          <div className="space-y-4">
            {STAGES.map((stage, i) => {
              const status =
                i < stageIdx  ? 'done' :
                i === stageIdx ? 'active' :
                'pending';
              return <ProcessingStep key={stage.id} stage={stage} status={status} />;
            })}
          </div>

          {stageIdx === STAGES.length - 1 && !processing && result && (
            <div className="mt-5 flex items-center gap-2 text-xs text-cyber-400 bg-cyber-900/20 border border-cyber-700/30 rounded-lg p-3">
              <CheckCircle2 className="w-4 h-4" />
              Analysis complete — {result.processing_time_ms}ms processing time
            </div>
          )}

          {error && (
            <div className="mt-5 flex items-center gap-2 text-xs text-red-400 bg-red-900/20 border border-red-700/30 rounded-lg p-3">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}

          {stageIdx === -1 && (
            <p className="text-xs text-slate-600 mt-6 font-mono text-center">
              Upload a PCAP or click "Load Demo" to begin
            </p>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4 animate-fade-in">
          {/* Summary cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <ResultCard
              icon={FileSearch} label="Packets Processed"
              value={result.packets_processed}
              color="border-cyber-700/30 stat-gradient-cyan"
            />
            <ResultCard
              icon={Wifi} label="HTTP Requests"
              value={result.http_requests_extracted}
              color="border-blue-700/30 stat-gradient-blue"
            />
            <ResultCard
              icon={Shield} label="Attacks Detected"
              value={result.attacks_detected}
              color="border-red-700/30 stat-gradient-red"
            />
            <ResultCard
              icon={Globe} label="High-Risk IPs"
              value={result.high_risk_ips}
              color="border-orange-700/30 stat-gradient-orange"
            />
          </div>

          {/* Detected attacks table */}
          <div className="glass-card border border-dark-600/50 overflow-hidden">
            <div className="px-5 py-4 border-b border-dark-700/50 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Detected Attacks
                <span className="ml-2 text-xs text-slate-500 font-mono">({result.attacks.length})</span>
              </h3>
              <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 rounded px-2 py-0.5">
                SIMULATED RESULTS
              </span>
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
                      <td className="font-mono text-xs text-slate-400 whitespace-nowrap">
                        {format(parseISO(atk.timestamp), 'MM/dd HH:mm:ss')}
                      </td>
                      <td className="font-mono text-xs text-cyber-400 whitespace-nowrap">{atk.source_ip}</td>
                      <td className="text-slate-300">{atk.attack_type}</td>
                      <td><RiskBadge severity={atk.severity} /></td>
                      <td>
                        <span className="text-xs font-mono text-slate-400">
                          {(atk.confidence * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td>
                        <span className={`text-xs font-mono font-semibold ${
                          atk.result === 'POTENTIAL_SUCCESS' ? 'text-red-400' : 'text-yellow-400'
                        }`}>
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
