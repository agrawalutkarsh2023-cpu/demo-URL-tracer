import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div style={{
      background: 'rgba(3, 12, 12, 0.95)',
      border: '1px solid rgba(3,83,82,0.35)',
      borderRadius: 10,
      padding: '10px 14px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: d.payload.fill, fontSize: 12, fontWeight: 600 }}>
        {d.name}:{' '}
        <span style={{ color: '#F3E8BC', fontWeight: 700 }}>{d.value}</span>
      </p>
    </div>
  );
};

/**
 * @param {Array}  data   - [{ name, value, fill }]
 * @param {number} [height]
 */
export default function SeverityChart({ data, height = 260 }) {
  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="48%"
          innerRadius={62}
          outerRadius={90}
          paddingAngle={4}
          dataKey="value"
          labelLine={false}
          stroke="transparent"
          strokeWidth={0}
        >
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.fill} stroke="transparent" />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          iconType="circle"
          iconSize={7}
          formatter={(val) => (
            <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{val}</span>
          )}
        />
        {/* Centre labels */}
        <text
          x="50%" y="44%"
          textAnchor="middle" dominantBaseline="middle"
          fill="#F3E8BC" fontSize={24} fontWeight={700}
          fontFamily="JetBrains Mono, monospace"
        >
          {total}
        </text>
        <text
          x="50%" y="53%"
          textAnchor="middle" dominantBaseline="middle"
          fill="var(--text-muted)" fontSize={11}
        >
          Total
        </text>
      </PieChart>
    </ResponsiveContainer>
  );
}
