import AdminSidebar from './AdminSidebar';

export default function AdminLayout({ children, title, subtitle }) {
    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <AdminSidebar />

            <main className="dashboard-main">
                <div className="dashboard-container">
                    <header className="dashboard-header">
                        <div>
                            <h1 className="dashboard-title">{title}</h1>
                            <p className="dashboard-subtitle">{subtitle}</p>
                        </div>
                    </header>
                    {children}
                </div>
            </main>
        </div>
    );
}
