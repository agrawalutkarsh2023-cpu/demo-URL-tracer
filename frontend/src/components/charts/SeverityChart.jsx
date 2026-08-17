import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 shadow-2xl">
      <p className="text-xs font-semibold" style={{ color: d.payload.fill }}>
        {d.name}: <span className="text-white">{d.value}</span>
      </p>
    </div>
  );
};

const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value, name }) => {
  const RADIAN = Math.PI / 180;
  const r = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + r * Math.cos(-midAngle * RADIAN);
  const y = cy + r * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={12} fontWeight={600}>
      {value}
    </text>
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
          innerRadius={65}
          outerRadius={95}
          paddingAngle={3}
          dataKey="value"
          labelLine={false}
          label={renderLabel}
        >
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.fill} stroke="transparent" />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(val) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{val}</span>}
        />
        {/* Centre label */}
        <text
          x="50%" y="46%" textAnchor="middle" dominantBaseline="middle"
          fill="#fff" fontSize={22} fontWeight={700}
        >
          {total}
        </text>
        <text
          x="50%" y="54%" textAnchor="middle" dominantBaseline="middle"
          fill="#64748b" fontSize={11}
        >
          Total
        </text>
      </PieChart>
    </ResponsiveContainer>
  );
}
