import { useEffect, useState } from 'react';

interface Job {
  id: string;
  source_id: string | null;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  total_rules: number;
  passed_rules: number;
  failed_rules: number;
}

export default function History() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    fetch('/api/jobs')
      .then(r => r.json())
      .then(data => setJobs(data.items || []))
      .catch(console.error);
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'failed': return 'bg-red-100 text-red-700';
      case 'running': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Run History</h2>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 font-medium">Job ID</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Started</th>
              <th className="px-4 py-3 font-medium">Rules</th>
              <th className="px-4 py-3 font-medium">Passed</th>
              <th className="px-4 py-3 font-medium">Failed</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(job => (
              <tr key={job.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-sm">{job.id.slice(0, 8)}...</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs ${statusColor(job.status)}`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {job.started_at ? new Date(job.started_at).toLocaleString() : '—'}
                </td>
                <td className="px-4 py-3">{job.total_rules}</td>
                <td className="px-4 py-3 text-green-600">{job.passed_rules}</td>
                <td className="px-4 py-3 text-red-600">{job.failed_rules}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
