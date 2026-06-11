import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminProyecciones() {
  const [proyecciones, setProyecciones] = useState([])
  const [peliculas, setPeliculas] = useState([])
  const [salas, setSalas] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [form, setForm] = useState({ IdPelicula: '', IdSala: '', IdEdicion: '', FechaHora: '', TieneQA: false })
  const [msg, setMsg] = useState('')
  const [isError, setIsError] = useState(false)

  const load = () => api.getProyecciones().then(setProyecciones)
  useEffect(() => {
    load()
    Promise.all([api.getPeliculas(), api.getSalas(), api.getEdiciones()])
      .then(([p, s, e]) => { setPeliculas(p); setSalas(s); setEdiciones(e) })
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await api.createProyeccion({ ...form, IdPelicula: parseInt(form.IdPelicula), IdSala: parseInt(form.IdSala), IdEdicion: parseInt(form.IdEdicion) })
      setMsg(res.message || 'Proyección programada exitosamente')
      setIsError(false)
      setForm({ IdPelicula: '', IdSala: '', IdEdicion: '', FechaHora: '', TieneQA: false })
      load()
    } catch (err) {
      setMsg(err.message)
      setIsError(true)
    }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Programación de Proyecciones</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Programe películas en salas y sedes específicas asignándolas a una edición.
          </p>
        </div>
        {msg && (
          <div style={{ 
            padding: '8px 16px', 
            background: isError ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)', 
            border: isError ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(16, 185, 129, 0.3)', 
            borderRadius: 8, 
            fontSize: 13, 
            color: isError ? '#fb7185' : '#34d399', 
            fontWeight: 600 
          }}>
            {msg}
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>Programar Nueva Fecha</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Película Seleccionada *</label>
              <select className="select" value={form.IdPelicula} onChange={e => setForm({ ...form, IdPelicula: e.target.value })} required>
                <option value="">Seleccione película...</option>
                {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Sala de Exhibición *</label>
              <select className="select" value={form.IdSala} onChange={e => setForm({ ...form, IdSala: e.target.value })} required>
                <option value="">Seleccione sala...</option>
                {salas.map(s => <option key={s.IdSala} value={s.IdSala}>{s.NombreSala} ({s.NombreSede})</option>)}
              </select>
            </div>



            <div className="form-group">
              <label className="form-label">Edición del Festival *</label>
              <select className="select" value={form.IdEdicion} onChange={e => setForm({ ...form, IdEdicion: e.target.value })} required>
                <option value="">Seleccione edición...</option>
                {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Fecha y Hora *</label>
              <input type="datetime-local" className="input" value={form.FechaHora} onChange={e => setForm({ ...form, FechaHora: e.target.value })} required />
            </div>

            <div className="form-group">
              <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <input type="checkbox" checked={form.TieneQA} onChange={e => setForm({ ...form, TieneQA: e.target.checked })} style={{ accentColor: 'var(--accent-purple)' }} />
                Incluye Conversatorio Q&A con Director/Elenco
              </label>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
              Programar Función
            </button>
          </form>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Película</th>
                <th>Sala / Ubicación</th>
                <th>Fecha y Hora</th>
                <th>Aforo Disponible</th>
                <th>Q&A</th>
              </tr>
            </thead>
            <tbody>
              {proyecciones.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                    No hay proyecciones programadas en esta edición.
                  </td>
                </tr>
              ) : (
                proyecciones.map(p => (
                  <tr key={p.IdProyeccion}>
                    <td style={{ fontWeight: 600 }}>{p.Titulo}</td>
                    <td>
                      <div>{p.NombreSala}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{p.NombreSede}</div>
                    </td>
                    <td>{new Date(p.FechaHora).toLocaleString('es-BO', { dateStyle: 'medium', timeStyle: 'short' })}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{p.AforoDisponible} / {p.Capacidad}</span>
                        <div style={{ width: 60, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                          <div style={{ 
                            height: '100%', 
                            width: `${Math.max(0, Math.min(100, (p.AforoDisponible / p.Capacidad) * 100))}%`, 
                            background: p.AforoDisponible === 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)' 
                          }} />
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${p.TieneQA ? 'badge-premiada' : 'badge-postulada'}`}>
                        {p.TieneQA ? 'Sí' : 'No'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

