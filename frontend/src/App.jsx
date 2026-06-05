import { Routes, Route, NavLink } from 'react-router-dom'
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

export default function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', minHeight: '100vh', background: '#f5f5f5' }}>
      <header style={{ background: '#1a1a2e', color: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', gap: 32 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700 }}>FestCine</h1>
        <nav style={{ display: 'flex', gap: 16, padding: '12px 0' }}>
          <NavLink to="/" end style={linkStyle}>Catálogo</NavLink>
          <NavLink to="/proyecciones" style={linkStyle}>Proyecciones</NavLink>
          <NavLink to="/comprar-entrada" style={linkStyle}>Comprar Entrada</NavLink>
          <NavLink to="/vender-abono" style={linkStyle}>Vender Abono</NavLink>
          <NavLink to="/reportes" style={linkStyle}>Reportes</NavLink>
          <span style={{ color: '#666', margin: '0 8px' }}>|</span>
          <NavLink to="/admin/peliculas" style={linkStyle}>Admin</NavLink>
        </nav>
      </header>
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
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
        </Routes>
      </main>
    </div>
  )
}

const linkStyle = {
  color: '#ccc', textDecoration: 'none', fontSize: 14, fontWeight: 500, padding: '4px 8px', borderRadius: 4, transition: 'all 0.2s'
}
