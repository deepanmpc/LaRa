import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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

                {/* Admin Routes */}
                <Route
                    path="/dashboard/admin"
                    element={
                        <ProtectedRoute requiredRole="ROLE_ADMIN">
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
