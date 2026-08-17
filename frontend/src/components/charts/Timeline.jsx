import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(3, 12, 12, 0.95)',
      border: '1px solid rgba(3,83,82,0.35)',
      borderRadius: 10,
      padding: '10px 14px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: '#F3E8BC', fontSize: 12, fontWeight: 600, marginBottom: 6 }}>{label}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
          {p.name}: <span style={{ color: p.color, fontWeight: 700 }}>{p.value}</span>
        </p>
      ))}
    </div>
  );
};

/**
 * @param {Array}  data   - [{ date, attacks, requests }]
 * @param {number} [height]
 */
export default function Timeline({ data, height = 240 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="gradAttacks" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#f87171" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#f87171" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradRequests" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#035352" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#035352" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(3,83,82,0.10)" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          iconType="circle"
          iconSize={7}
          formatter={(val) => <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{val}</span>}
        />
        <Area
          type="monotone"
          dataKey="requests"
          name="Requests"
          stroke="#035352"
          strokeWidth={2}
          fill="url(#gradRequests)"
          dot={false}
          activeDot={{ r: 4, fill: '#F3E8BC', stroke: '#035352', strokeWidth: 2 }}
        />
        <Area
          type="monotone"
          dataKey="attacks"
          name="Attacks"
          stroke="#f87171"
          strokeWidth={2}
          fill="url(#gradAttacks)"
          dot={false}
          activeDot={{ r: 4, fill: '#f87171' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
