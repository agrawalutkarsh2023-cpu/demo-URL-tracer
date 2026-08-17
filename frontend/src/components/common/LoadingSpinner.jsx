import { Shield } from 'lucide-react';

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-5 text-center">
      <div className="relative">
        <div className="w-14 h-14 rounded-full border-2 border-dark-600 border-t-cyber-500 animate-spin" />
        <Shield className="absolute inset-0 m-auto w-5 h-5 text-cyber-600" />
      </div>
      <p className="text-sm text-slate-500 font-mono animate-pulse">{message}</p>
    </div>
  );
}
