import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Rules from './pages/Rules';
import History from './pages/History';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-8">
            <h1 className="text-xl font-bold text-blue-600">DQ Platform</h1>
            <Link to="/" className="text-gray-700 hover:text-blue-600">Dashboard</Link>
            <Link to="/rules" className="text-gray-700 hover:text-blue-600">Rules</Link>
            <Link to="/history" className="text-gray-700 hover:text-blue-600">History</Link>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
