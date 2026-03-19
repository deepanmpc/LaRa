import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import FamilyDashboard from './pages/FamilyDashboard';
import ClinicianPending from './pages/ClinicianPending';
import ProtectedRoute from './components/ProtectedRoute';
import ChildrenList from './pages/dashboard/ChildrenList';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import ClinicianDashboard from './pages/dashboard/ClinicianDashboard';
import ClinicianStudents from './pages/dashboard/ClinicianStudents';
import ClinicianStudentDetail from './pages/dashboard/ClinicianStudentDetail';
import ClinicianReports from './pages/dashboard/ClinicianReports';
import ClinicalSessions from './pages/dashboard/ClinicalSessions';
import Profile from './pages/dashboard/Profile';
import VoiceSessionPage from './pages/voice/VoiceSessionPage';

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Landing />} />
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
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="PENDING">
                            <ClinicianPending />
                        </ProtectedRoute>
                    }
                />
                {/* Clinician Dashboard Routes */}
                <Route
                    path="/dashboard/clinical"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="APPROVED">
                            <ClinicianDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/clinical/students"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="APPROVED">
                            <ClinicianStudents />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/clinical/student/:id"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="APPROVED">
                            <ClinicianStudentDetail />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/clinical/reports"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="APPROVED">
                            <ClinicianReports />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/clinical/sessions"
                    element={
                        <ProtectedRoute requiredRole="ROLE_CLINICIAN" requiredStatus="APPROVED">
                            <ClinicalSessions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/profile"
                    element={
                        <ProtectedRoute>
                            <Profile />
                        </ProtectedRoute>
                    }
                />

                {/* Admin Routes */}
                <Route
                    path="/dashboard/admin"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />
                
                {/* Voice Kiosk Flow (ChatGPT Style) */}
                <Route path="/voice-session/:childId/:sessionUuid" element={<VoiceSessionPage />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
