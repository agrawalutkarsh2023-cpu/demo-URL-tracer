import { AlertOctagon, AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

const CONFIG = {
  CRITICAL: {
    cls: 'badge-critical',
    Icon: AlertOctagon,
    dot: 'bg-red-500',
  },
  HIGH: {
    cls: 'badge-high',
    Icon: AlertTriangle,
    dot: 'bg-orange-500',
  },
  MEDIUM: {
    cls: 'badge-medium',
    Icon: AlertCircle,
    dot: 'bg-yellow-400',
  },
  LOW: {
    cls: 'badge-low',
    Icon: CheckCircle,
    dot: 'bg-green-400',
  },
};

/**
 * @param {'CRITICAL'|'HIGH'|'MEDIUM'|'LOW'} severity
 * @param {boolean} [showIcon]
 * @param {boolean} [dot] - show dot instead of icon
 */
export default function RiskBadge({ severity, showIcon = true, dot = false }) {
  const cfg = CONFIG[severity] ?? CONFIG.LOW;
  const { cls, Icon } = cfg;

  return (
    <span className={cls}>
      {dot ? (
        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} inline-block`} />
      ) : showIcon ? (
        <Icon className="w-3 h-3" />
      ) : null}
      {severity}
    </span>
  );
}
