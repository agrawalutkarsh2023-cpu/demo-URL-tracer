import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
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
      <p style={{ color: '#F3E8BC', fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
          {p.name}:{' '}
          <span style={{ color: '#F3E8BC', fontWeight: 700 }}>{p.value}</span>
        </p>
      ))}
    </div>
  );
};

// Brand-consistent color palette for bars
const BAR_COLORS = [
  '#035352', '#046a69', '#04817f', '#059894',
  '#06b0ac', '#07c8c3', '#1a8f8e', '#2b7070',
];

/**
 * @param {Array}  data  - [{ name, count, fill? }]
 * @param {string} [xKey]
 * @param {string} [yKey]
 * @param {number} [height]
 */
export default function AttackChart({ data, xKey = 'name', yKey = 'count', height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(3,83,82,0.12)" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          interval={0}
          angle={-30}
          textAnchor="end"
          height={52}
        />
        <YAxis
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          allowDecimals={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(3,83,82,0.07)' }} />
        <Bar dataKey={yKey} radius={[5, 5, 0, 0]} name="Attacks">
          {data.map((entry, index) => (
            <Cell
              key={index}
              fill={entry.fill ?? BAR_COLORS[index % BAR_COLORS.length]}
              opacity={0.85}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
