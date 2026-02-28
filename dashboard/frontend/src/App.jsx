import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';

import Overview from './pages/Overview';
import Emotions from './pages/Emotions';
import PredictivePanel from './pages/PredictivePanel';
import Interventions from './pages/Interventions';
import XAI from './pages/XAI';
import GraphPage from './pages/GraphPage';
import SystemIntegrity from './pages/SystemIntegrity';
import SimulationSandbox from './pages/SimulationSandbox';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Overview />} />
          <Route path="emotions" element={<Emotions />} />
          <Route path="predictive" element={<PredictivePanel />} />
          <Route path="interventions" element={<Interventions />} />
          <Route path="xai" element={<XAI />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="sandbox" element={<SimulationSandbox />} />
          <Route path="integrity" element={<SystemIntegrity />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
