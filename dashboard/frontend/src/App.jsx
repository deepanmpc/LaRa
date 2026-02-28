import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';

// Mock page components until implementation
const Overview = () => <div className="p-8 bg-gray-800 rounded-xl border border-gray-700"><h1 className="text-2xl font-bold mb-4">Educational Progress & ZPD</h1><p className="text-slate-400">Implementation pending for Recharts.</p></div>;
const Emotions = () => <div className="p-8 bg-gray-800 rounded-xl border border-gray-700"><h1 className="text-2xl font-bold mb-4">Emotional Stability</h1></div>;
const XAI = () => <div className="p-8 bg-gray-800 rounded-xl border border-gray-700"><h1 className="text-2xl font-bold mb-4">Explainable AI</h1></div>;
const Interventions = () => <div className="p-8 bg-gray-800 rounded-xl border border-gray-700"><h1 className="text-2xl font-bold mb-4">Tool Intelligence</h1></div>;
const GraphPage = () => <div className="p-8 bg-gray-800 rounded-xl border border-gray-700"><h1 className="text-2xl font-bold mb-4">3D Knowledge Graph</h1></div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Overview />} />
          <Route path="emotions" element={<Emotions />} />
          <Route path="xai" element={<XAI />} />
          <Route path="interventions" element={<Interventions />} />
          <Route path="graph" element={<GraphPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
