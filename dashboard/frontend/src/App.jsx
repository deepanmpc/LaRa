import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/ClinicianLayout';
import CaregiverLayout from './layouts/CaregiverLayout';

import Overview from './pages/Overview';
import Emotions from './pages/Emotions';
import PredictivePanel from './pages/PredictivePanel';
import Interventions from './pages/Interventions';
import XAI from './pages/XAI';
import GraphPage from './pages/GraphPage';
import SystemIntegrity from './pages/SystemIntegrity';
import SimulationSandbox from './pages/SimulationSandbox';
import SessionLauncher from './pages/SessionLauncher';
import SimpleAnalytics from './pages/SimpleAnalytics';
import ClinicalDashboard from './pages/dashboard/clinical';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Caregiver Flow (Tier 1) */}
        <Route path="/dashboard" element={<CaregiverLayout />}>
          <Route path="simple" element={<SimpleAnalytics />} />
        </Route>

        {/* Clinical Flow (Tier 2 Hybrid) */}
        <Route path="/dashboard/clinical" element={<ClinicalDashboard />} />

        <Route path="/session" element={<SessionLauncher />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Overview />} />
          <Route path="emotions" element={<Emotions />} />
          <Route path="predictive" element={<PredictivePanel />} />
          <Route path="interventions" element={<Interventions />} />
          <Route path="xai-logs" element={<XAI />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="sandbox" element={<SimulationSandbox />} />
          <Route path="integrity" element={<SystemIntegrity />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
