import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DimensionScore {
  dimension: string;
  score: number;
  total_checks: number;
  passed_checks: number;
}

interface Props {
  dimensions: DimensionScore[];
}

export default function DimensionChart({ dimensions }: Props) {
  const data = dimensions.map(d => ({
    name: d.dimension.charAt(0).toUpperCase() + d.dimension.slice(1),
    score: d.score,
    checks: d.total_checks,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
