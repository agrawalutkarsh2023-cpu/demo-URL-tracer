import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 shadow-2xl">
      <p className="text-xs font-semibold text-slate-300 mb-1">{label}</p>
      {payload.map(p => (
        <p key={p.name} className="text-xs" style={{ color: p.fill ?? '#00cc8f' }}>
          {p.name}: <span className="font-bold">{p.value}</span>
        </p>
      ))}
    </div>
  );
};

/**
 * @param {Array}  data  - [{ name, count, fill }]
 * @param {string} [xKey]
 * @param {string} [yKey]
 * @param {number} [height]
 */
export default function AttackChart({ data, xKey = 'name', yKey = 'count', height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1a2340" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          interval={0}
          angle={-30}
          textAnchor="end"
          height={52}
        />
        <YAxis
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          allowDecimals={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,204,143,0.05)' }} />
        <Bar dataKey={yKey} radius={[4, 4, 0, 0]} name="Attacks">
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.fill ?? '#00cc8f'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
