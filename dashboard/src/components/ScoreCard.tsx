interface ScoreCardProps {
  title: string;
  score: number;
  unit?: string;
  label?: string;
}

export default function ScoreCard({ title, score, unit = '%', label }: ScoreCardProps) {
  const color = score >= 90 ? 'text-green-600' :
                score >= 70 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-sm text-gray-500 uppercase tracking-wide">{title}</p>
      {label ? (
        <p className="text-lg font-semibold mt-1">{label}</p>
      ) : (
        <p className={`text-3xl font-bold mt-1 ${color}`}>
          {typeof score === 'number' ? score.toFixed(1) : score}{unit}
        </p>
      )}
    </div>
  );
}
