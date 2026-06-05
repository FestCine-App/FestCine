import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminEventos() {
  const [eventos, setEventos] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [personal, setPersonal] = useState([])
  const [form, setForm] = useState({ IdEdicion: '', NombreEvento: '', TipoEvento: 'Masterclass', FechaHora: '', Aforo: '', CostoInscripcion: '0', expositores: [] })
  const [msg, setMsg] = useState('')

  const load = () => api.getEventos().then(setEventos)
  useEffect(() => {
    load()
    Promise.all([api.getEdiciones(), api.getPersonal()])
      .then(([e, p]) => { setEdiciones(e); setPersonal(p) })
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
      await api.createEvento({ ...form, Aforo: parseInt(form.Aforo), CostoInscripcion: parseFloat(form.CostoInscripcion), IdEdicion: parseInt(form.IdEdicion) })
      setMsg('Evento creado')
      setForm({ IdEdicion: '', NombreEvento: '', TipoEvento: 'Masterclass', FechaHora: '', Aforo: '', CostoInscripcion: '0', expositores: [] })
      load()
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Registrar Evento</h2>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
        <div style={{ marginBottom: 12 }}>
          <select style={inp} value={form.IdEdicion} onChange={e => setForm({ ...form, IdEdicion: e.target.value })} required>
            <option value="">Edición</option>
            {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <input placeholder="Nombre del Evento" style={inp} value={form.NombreEvento} onChange={e => setForm({ ...form, NombreEvento: e.target.value })} required />
        </div>
        <div style={{ marginBottom: 12 }}>
          <select style={inp} value={form.TipoEvento} onChange={e => setForm({ ...form, TipoEvento: e.target.value })}>
            {['Masterclass','Taller','Coctel'].map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <input type="datetime-local" style={inp} value={form.FechaHora} onChange={e => setForm({ ...form, FechaHora: e.target.value })} required />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input placeholder="Aforo" type="number" style={inp} value={form.Aforo} onChange={e => setForm({ ...form, Aforo: e.target.value })} required />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input placeholder="Costo (0 si gratuito)" type="number" step="0.01" style={inp} value={form.CostoInscripcion} onChange={e => setForm({ ...form, CostoInscripcion: e.target.value })} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: 13, fontWeight: 600, display: 'block', marginBottom: 4 }}>Expositores</label>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {personal.map(p => (
              <label key={p.IdPersonal} style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
                <input type="checkbox" checked={form.expositores.includes(p.IdPersonal)} onChange={() => toggleExpositor(p.IdPersonal)} />
                {p.Nombre}
              </label>
            ))}
          </div>
        </div>
        <button type="submit" style={btn}>Crear Evento</button>
        {msg && <p style={{ fontSize: 13, marginTop: 8 }}>{msg}</p>}
      </form>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead style={{ background: '#1a1a2e', color: '#fff' }}>
          <tr><th style={th}>Nombre</th><th style={th}>Tipo</th><th style={th}>Fecha</th><th style={th}>Aforo</th><th style={th}>Expositores</th></tr>
        </thead>
        <tbody>
          {eventos.map(e => (
            <tr key={e.IdEvento} style={{ borderBottom: '1px solid #eee' }}>
              <td style={td}>{e.NombreEvento}</td><td style={td}>{e.TipoEvento}</td>
              <td style={td}>{new Date(e.FechaHora).toLocaleString('es-BO')}</td>
              <td style={td}>{e.Aforo}</td><td style={td}>{e.Expositores}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const inp = { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btn = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
const th = { padding: '8px 12px', textAlign: 'left', fontSize: 13 }
const td = { padding: '8px 12px', fontSize: 13 }
