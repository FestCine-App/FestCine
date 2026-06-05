import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminEventos() {
  const [eventos, setEventos] = useState([])
  const [personal, setPersonal] = useState([])
  const [form, setForm] = useState({ NombreEvento: '', TipoEvento: 'Masterclass', FechaHora: '', Aforo: '', CostoInscripcion: '0', expositores: [] })
  const [msg, setMsg] = useState('')

  const load = () => api.getEventos().then(setEventos)
  useEffect(() => {
    load()
    api.getPersonal().then(setPersonal)
  }, [])

  const toggleExpositor = (id) => {
    setForm(prev => ({
      ...prev,
      expositores: prev.expositores.includes(id) ? prev.expositores.filter(e => e !== id) : [...prev.expositores, id]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.createEvento({ ...form, Aforo: parseInt(form.Aforo), CostoInscripcion: parseFloat(form.CostoInscripcion) })
      setMsg('Evento paralelo programado exitosamente')
      setForm({ NombreEvento: '', TipoEvento: 'Masterclass', FechaHora: '', Aforo: '', CostoInscripcion: '0', expositores: [] })
      load()
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Gestión de Eventos Paralelos</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Organice talleres, masterclasses, paneles de discusión y eventos de networking del festival.
          </p>
        </div>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: 24, alignItems: 'start' }}>
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>Programar Evento</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nombre del Evento *</label>
              <input placeholder="Ej. Taller de Dirección de Fotografía" className="input" value={form.NombreEvento} onChange={e => setForm({ ...form, NombreEvento: e.target.value })} required />
            </div>

            <div className="grid-2" style={{ marginBottom: 16 }}>
              <div>
                <label className="form-label">Tipo de Evento *</label>
                <select className="select" value={form.TipoEvento} onChange={e => setForm({ ...form, TipoEvento: e.target.value })}>
                  {['Masterclass','Taller','Coctel','Panel','Foro'].map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="form-label">Fecha y Hora *</label>
                <input type="datetime-local" className="input" value={form.FechaHora} onChange={e => setForm({ ...form, FechaHora: e.target.value })} required />
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: 16 }}>
              <div>
                <label className="form-label">Aforo *</label>
                <input placeholder="Ej. 50" type="number" className="input" value={form.Aforo} onChange={e => setForm({ ...form, Aforo: e.target.value })} required />
              </div>
              <div>
                <label className="form-label">Costo (Bs.) *</label>
                <input placeholder="0 si es gratuito" type="number" step="0.01" className="input" value={form.CostoInscripcion} onChange={e => setForm({ ...form, CostoInscripcion: e.target.value })} />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Ponentes / Expositores</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 6, maxHeight: 150, overflowY: 'auto', background: 'rgba(0,0,0,0.2)', padding: 12, borderRadius: 8, border: '1px solid rgba(255,255,255,0.04)' }}>
                {personal.length === 0 ? (
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>No hay personal registrado</span>
                ) : (
                  personal.map(p => (
                    <label key={p.IdPersonal} style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', color: 'var(--text-secondary)' }}>
                      <input type="checkbox" checked={form.expositores.includes(p.IdPersonal)} onChange={() => toggleExpositor(p.IdPersonal)} style={{ accentColor: 'var(--accent-purple)' }} />
                      {p.Nombre}
                    </label>
                  ))
                )}
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
              Crear Evento
            </button>
          </form>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Nombre Evento</th>
                <th>Tipo</th>
                <th>Fecha y Hora</th>
                <th>Costo / Aforo</th>
                <th>Expositores</th>
              </tr>
            </thead>
            <tbody>
              {eventos.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                    No hay eventos programados todavía.
                  </td>
                </tr>
              ) : (
                eventos.map(e => (
                  <tr key={e.IdEvento}>
                    <td style={{ fontWeight: 600 }}>{e.NombreEvento}</td>
                    <td>
                      <span className={`badge ${
                        e.TipoEvento === 'Masterclass' ? 'badge-premiada' :
                        e.TipoEvento === 'Taller' ? 'badge-seleccionada' : 'badge-postulada'
                      }`}>
                        {e.TipoEvento}
                      </span>
                    </td>
                    <td>{new Date(e.FechaHora).toLocaleString('es-BO', { dateStyle: 'medium', timeStyle: 'short' })}</td>
                    <td style={{ fontSize: 13 }}>
                      <div>Aforo: {e.Aforo}</div>
                      <div style={{ color: parseFloat(e.CostoInscripcion) > 0 ? 'var(--accent-emerald)' : 'var(--text-secondary)' }}>
                        {parseFloat(e.CostoInscripcion) > 0 ? `Bs. ${parseFloat(e.CostoInscripcion).toFixed(2)}` : 'Gratuito'}
                      </div>
                    </td>
                    <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                      {e.Expositores || '-'}
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

