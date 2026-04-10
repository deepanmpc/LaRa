import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import FamilyDashboard from './pages/FamilyDashboard';
import LiveMonitorPage from './pages/family/LiveMonitorPage';
import ClinicianPending from './pages/ClinicianPending';
import ProtectedRoute from './components/ProtectedRoute';
import ChildrenList from './pages/dashboard/ChildrenList';
import ClinicianDashboard from './pages/dashboard/ClinicianDashboard';
import ClinicianStudents from './pages/dashboard/ClinicianStudents';
import ClinicianStudentDetail from './pages/dashboard/ClinicianStudentDetail';
import ClinicianReports from './pages/dashboard/ClinicianReports';
import ClinicalSessions from './pages/dashboard/ClinicalSessions';
import Profile from './pages/dashboard/Profile';
import VoiceSessionPage from './pages/voice/VoiceSessionPage';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminSystemMonitoring from './pages/admin/AdminSystemMonitoring';
import AdminModelEvaluation from './pages/admin/AdminModelEvaluation';
import AdminDatasetExport from './pages/admin/AdminDatasetExport';
import AdminPopulationAnalytics from './pages/admin/AdminPopulationAnalytics';
import AdminAlertMonitoring from './pages/admin/AdminAlertMonitoring';
import AdminUserManagement from './pages/admin/AdminUserManagement';

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
                    path="/live-monitor/:childId/:sessionUuid"
                    element={
                        <ProtectedRoute requiredRole="ROLE_FAMILY">
                            <LiveMonitorPage />
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

                {/* Admin Workspace Routes */}
                <Route
                    path="/admin"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/system"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminSystemMonitoring />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/model"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminModelEvaluation />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/dataset"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminDatasetExport />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/population"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminPopulationAnalytics />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/alerts"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminAlertMonitoring />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/users"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminUserManagement />
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
