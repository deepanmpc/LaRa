import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import FamilyDashboard from './pages/FamilyDashboard';
import ClinicianPending from './pages/ClinicianPending';
import ProtectedRoute from './components/ProtectedRoute';
import ChildrenList from './pages/dashboard/ChildrenList';
import ChildSessionPage from './pages/child/ChildSessionPage';

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route
                    path="/dashboard/children"
                    element={
                        <ProtectedRoute requiredRole="ROLE_FAMILY">
                            <ChildrenList />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/family/:childId"
                    element={
                        <ProtectedRoute requiredRole="ROLE_FAMILY">
                            <FamilyDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/clinician/pending"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN">
                            <ClinicianPending />
                        </ProtectedRoute>
                    }
                />
                
                {/* Child Fullscreen Kiosk Flow (Phase 1) */}
                <Route path="/child-session/:childId/:sessionUuid" element={<ChildSessionPage />} />

                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
