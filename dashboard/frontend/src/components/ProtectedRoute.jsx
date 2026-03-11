import { Navigate } from 'react-router-dom';
import { getStoredUser, isAuthenticated } from '../services/authService';

export default function ProtectedRoute({ children, requiredRole, requiredStatus }) {
    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    const user = getStoredUser();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // Role mismatch: send them to their role's home
    if (requiredRole && user.role !== requiredRole) {
        if (user.role === 'ROLE_FAMILY') {
            return <Navigate to="/dashboard/children" replace />;
        }
        if (user.role === 'ROLE_CLINICIAN') {
            return user.status === 'APPROVED'
                ? <Navigate to="/dashboard/clinical" replace />
                : <Navigate to="/clinician/pending" replace />;
        }
        if (user.role === 'ROLE_ADMIN') {
            return <Navigate to="/dashboard/admin" replace />;
        }
        return <Navigate to="/login" replace />;
    }

    // Role matches, but check status if required
    if (requiredStatus && user.status !== requiredStatus) {
        if (user.role === 'ROLE_CLINICIAN') {
            return user.status === 'APPROVED'
                ? <Navigate to="/dashboard/clinical" replace />
                : <Navigate to="/clinician/pending" replace />;
        }
        return <Navigate to="/login" replace />;
    }

    return children;
}
