import { useRef, useState } from 'react';
import { Upload, File, X, AlertCircle } from 'lucide-react';

/**
 * @param {Function} onFile  - called with File object when selected
 * @param {string}   accept  - file accept string e.g. '.pcap,.cap'
 * @param {string}   label
 * @param {string}   hint
 */
export default function FileUpload({ onFile, accept = '.pcap,.cap', label = 'Upload File', hint = '' }) {
  const inputRef  = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [selected, setSelected] = useState(null);
  const [error, setError]       = useState('');

  const validateAndSet = (file) => {
    setError('');
    if (!file) return;
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    const allowed = accept.split(',').map(s => s.trim().toLowerCase());
    if (!allowed.includes(ext)) {
      setError(`Invalid file type. Allowed: ${accept}`);
      return;
    }
    setSelected(file);
    onFile(file);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    validateAndSet(e.dataTransfer.files[0]);
  };

  const clear = (e) => {
    e.stopPropagation();
    setSelected(null);
    setError('');
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div>
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''} ${selected ? 'border-cyber-600/60 bg-cyber-900/10' : ''}`}
        onClick={() => !selected && inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={e => validateAndSet(e.target.files[0])}
        />

        {selected ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-xl bg-cyber-900/40 border border-cyber-600/40 flex items-center justify-center">
              <File className="w-7 h-7 text-cyber-400" />
            </div>
            <div className="text-center">
              <p className="text-sm font-semibold text-white">{selected.name}</p>
              <p className="text-xs text-slate-500 mt-1">
                {(selected.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button onClick={clear} className="btn-secondary text-xs gap-1.5 px-3 py-1.5">
              <X className="w-3.5 h-3.5" />
              Remove
            </button>
          </div>
        ) : (
          <>
            <div className="w-14 h-14 rounded-xl bg-dark-700 border border-dark-600 flex items-center justify-center">
              <Upload className="w-7 h-7 text-slate-500" />
            </div>
            <div className="text-center">
              <p className="text-base font-semibold text-slate-300">{label}</p>
              <p className="text-sm text-slate-500 mt-1">
                Drag &amp; drop or <span className="text-cyber-400 underline underline-offset-2">browse</span>
              </p>
              {hint && <p className="text-xs text-slate-600 mt-2">{hint}</p>}
              <p className="text-xs text-slate-600 mt-1">Accepted: {accept}</p>
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="mt-2 flex items-center gap-2 text-xs text-red-400">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
