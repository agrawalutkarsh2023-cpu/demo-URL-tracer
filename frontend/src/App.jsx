import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout         from './components/layout/Layout.jsx';
import Dashboard      from './pages/Dashboard.jsx';
import AttackExplorer from './pages/AttackExplorer.jsx';
import IPIntelligence from './pages/IPIntelligence.jsx';
import PCAPAnalysis   from './pages/PCAPAnalysis.jsx';
import Reports        from './pages/Reports.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"                 element={<Dashboard />} />
          <Route path="/attacks"          element={<AttackExplorer />} />
          <Route path="/ip-intelligence"  element={<IPIntelligence />} />
          <Route path="/pcap"             element={<PCAPAnalysis />} />
          <Route path="/reports"          element={<Reports />} />
          {/* Fallback */}
          <Route path="*"                 element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
