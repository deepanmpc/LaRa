import { Navigate } from 'react-router-dom';
import { getStoredUser, isAuthenticated } from '../services/authService';

export default function ProtectedRoute({ children, requiredRole }) {
    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    const user = getStoredUser();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (requiredRole && user.role !== requiredRole) {
        // Route to the appropriate dashboard for the user's role
        if (user.role === 'ROLE_FAMILY') {
            return <Navigate to="/dashboard/children" replace />;
        }
        if (user.role === 'ROLE_CLINICIAN') {
            return <Navigate to="/clinician/pending" replace />;
        }
        return <Navigate to="/login" replace />;
    }

    return children;
}
