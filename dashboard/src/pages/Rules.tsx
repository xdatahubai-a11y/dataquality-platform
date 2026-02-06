import { useEffect, useState } from 'react';

interface Rule {
  id: string;
  name: string;
  dimension: string;
  column_name: string | null;
  threshold: number | null;
  severity: string;
  is_active: boolean;
}

export default function Rules() {
  const [rules, setRules] = useState<Rule[]>([]);

  useEffect(() => {
    fetch('/api/rules')
      .then(r => r.json())
      .then(data => setRules(data.items || []))
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">DQ Rules</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          + New Rule
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Dimension</th>
              <th className="px-4 py-3 font-medium">Column</th>
              <th className="px-4 py-3 font-medium">Threshold</th>
              <th className="px-4 py-3 font-medium">Severity</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {rules.map(rule => (
              <tr key={rule.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3">{rule.name}</td>
                <td className="px-4 py-3 capitalize">{rule.dimension}</td>
                <td className="px-4 py-3">{rule.column_name || '—'}</td>
                <td className="px-4 py-3">{rule.threshold ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs ${
                    rule.severity === 'critical' ? 'bg-red-100 text-red-700' :
                    rule.severity === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>{rule.severity}</span>
                </td>
                <td className="px-4 py-3">
                  <span className={rule.is_active ? 'text-green-600' : 'text-gray-400'}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
