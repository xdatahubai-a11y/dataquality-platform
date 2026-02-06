import { useEffect, useState } from 'react';
import ScoreCard from '../components/ScoreCard';
import DimensionChart from '../components/DimensionChart';

interface DimensionScore {
  dimension: string;
  score: number;
  total_checks: number;
  passed_checks: number;
}

interface Summary {
  overall_score: number;
  dimensions: DimensionScore[];
  total_runs: number;
  last_run_at: string | null;
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    fetch('/api/metrics/summary')
      .then(r => r.json())
      .then(setSummary)
      .catch(console.error);
  }, []);

  if (!summary) return <div className="text-center py-12">Loading...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Data Quality Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard title="Overall Score" score={summary.overall_score} />
        <ScoreCard title="Total Runs" score={summary.total_runs} unit="" />
        <ScoreCard
          title="Last Run"
          score={0}
          label={summary.last_run_at ? new Date(summary.last_run_at).toLocaleString() : 'Never'}
        />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Dimension Scores</h3>
        <DimensionChart dimensions={summary.dimensions} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {summary.dimensions.map(d => (
          <ScoreCard key={d.dimension} title={d.dimension} score={d.score} />
        ))}
      </div>
    </div>
  );
}
