import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Catalogo from './pages/Catalogo'
import Proyecciones from './pages/Proyecciones'
import ComprarEntrada from './pages/ComprarEntrada'
import VenderAbono from './pages/VenderAbono'
import Reportes from './pages/Reportes'
import AdminPeliculas from './pages/AdminPeliculas'
import AdminProyecciones from './pages/AdminProyecciones'
import AdminEventos from './pages/AdminEventos'
import AdminJurados from './pages/AdminJurados'
import AdminPatrocinadores from './pages/AdminPatrocinadores'
import AdminSalas from './pages/AdminSalas'
import AdminPersonal from './pages/AdminPersonal'
import AdminEdiciones from './pages/AdminEdiciones'
import AdminAsistentes from './pages/AdminAsistentes'
import AdminLogistica from './pages/AdminLogistica'

export default function App() {
  const location = useLocation()
  const isAdminPath = location.pathname.startsWith('/admin')

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Premium Glassmorphic Header */}
      <header style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        background: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 72
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: 16,
            color: '#fff',
            boxShadow: '0 0 15px rgba(139, 92, 246, 0.5)'
          }}>
            F
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 800, background: 'linear-gradient(to right, #fff, var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
            FestCine
          </h1>
        </div>

        {/* Main Navigation */}
        <nav style={{ display: 'flex', gap: 8 }}>
          <NavLink to="/" end className="nav-link">Catálogo</NavLink>
          <NavLink to="/proyecciones" className="nav-link">Proyecciones</NavLink>
          <NavLink to="/comprar-entrada" className="nav-link">Comprar Entrada</NavLink>
          <NavLink to="/vender-abono" className="nav-link">Vender Abono</NavLink>
          <NavLink to="/reportes" className="nav-link">Reportes</NavLink>
          <span style={{ width: 1, background: 'rgba(255, 255, 255, 0.1)', margin: '4px 8px' }}></span>
          <NavLink to="/admin/peliculas" className="nav-link" style={({ isActive }) => {
            return isAdminPath ? {
              color: '#fff',
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.2)'
            } : {}
          }}>
            Panel Admin
          </NavLink>
        </nav>
      </header>

      {/* Admin Sub-navigation - displays dynamically when inside admin views */}
      {isAdminPath && (
        <div style={{
          background: 'rgba(10, 14, 26, 0.9)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          padding: '8px 24px',
          overflowX: 'auto',
          whiteSpace: 'nowrap'
        }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', gap: 6 }}>
            <NavLink to="/admin/peliculas" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Películas</NavLink>
            <NavLink to="/admin/salas" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Sedes/Salas</NavLink>
            <NavLink to="/admin/proyecciones" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Proyecciones</NavLink>
            <NavLink to="/admin/eventos" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Eventos Paralelos</NavLink>
            <NavLink to="/admin/jurados" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Jurados y Premios</NavLink>
            <NavLink to="/admin/patrocinadores" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Patrocinadores</NavLink>
            <NavLink to="/admin/personal" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Personal y Reparto</NavLink>
            <NavLink to="/admin/ediciones" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Ediciones</NavLink>
            <NavLink to="/admin/asistentes" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Asistentes/Abonos</NavLink>
            <NavLink to="/admin/logistica" className="nav-link" style={{ fontSize: 13, padding: '6px 12px' }}>Logística</NavLink>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main style={{ flex: 1, maxWidth: 1200, width: '100%', margin: '0 auto', padding: '32px 24px' }}>
        <Routes>
          <Route path="/" element={<Catalogo />} />
          <Route path="/proyecciones" element={<Proyecciones />} />
          <Route path="/comprar-entrada" element={<ComprarEntrada />} />
          <Route path="/vender-abono" element={<VenderAbono />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/admin/peliculas" element={<AdminPeliculas />} />
          <Route path="/admin/proyecciones" element={<AdminProyecciones />} />
          <Route path="/admin/eventos" element={<AdminEventos />} />
          <Route path="/admin/jurados" element={<AdminJurados />} />
          <Route path="/admin/patrocinadores" element={<AdminPatrocinadores />} />
          <Route path="/admin/salas" element={<AdminSalas />} />
          <Route path="/admin/personal" element={<AdminPersonal />} />
          <Route path="/admin/ediciones" element={<AdminEdiciones />} />
          <Route path="/admin/asistentes" element={<AdminAsistentes />} />
          <Route path="/admin/logistica" element={<AdminLogistica />} />
        </Routes>
      </main>

      {/* Premium Footer */}
      <footer style={{
        background: 'var(--bg-secondary)',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        padding: '24px',
        textAlign: 'center',
        color: 'var(--text-secondary)',
        fontSize: 13
      }}>
        <p>© 2026 FestCine — Sistema de Gestión de Festival de Cine. Todos los derechos reservados.</p>
        <p style={{ fontSize: 11, marginTop: 4, opacity: 0.6 }}>Motor: PostgreSQL 18 | Diseñado para Excelencia Visual</p>
      </footer>
    </div>
  )
}
