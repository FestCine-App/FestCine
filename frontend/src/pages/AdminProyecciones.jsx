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
      setMsg(res.message)
      setIsError(false)
      setForm({ IdPelicula: '', IdSala: '', IdEdicion: '', FechaHora: '', TieneQA: false })
      load()
    } catch (err) {
      setMsg(err.message)
      setIsError(true)
    }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Programar Proyección</h2>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 20, borderRadius: 8, marginBottom: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
        <div style={{ marginBottom: 12 }}>
          <select style={inp} value={form.IdPelicula} onChange={e => setForm({ ...form, IdPelicula: e.target.value })} required>
            <option value="">Película</option>
            {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <select style={inp} value={form.IdSala} onChange={e => setForm({ ...form, IdSala: e.target.value })} required>
            <option value="">Sala</option>
            {salas.map(s => <option key={s.IdSala} value={s.IdSala}>{s.NombreSala} - {s.NombreSede}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <select style={inp} value={form.IdEdicion} onChange={e => setForm({ ...form, IdEdicion: e.target.value })} required>
            <option value="">Edición</option>
            {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <input type="datetime-local" style={inp} value={form.FechaHora} onChange={e => setForm({ ...form, FechaHora: e.target.value })} required />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" checked={form.TieneQA} onChange={e => setForm({ ...form, TieneQA: e.target.checked })} />
            Incluye Q&A
          </label>
        </div>
        <button type="submit" style={btn}>Programar</button>
        {msg && <p style={{ fontSize: 13, marginTop: 8, color: isError ? '#c0392b' : '#27ae60', background: isError ? '#fce4e4' : '#e8f8e8', padding: '8px 12px', borderRadius: 4 }}>{msg}</p>}
      </form>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead style={{ background: '#1a1a2e', color: '#fff' }}>
          <tr><th style={th}>Película</th><th style={th}>Sala</th><th style={th}>Fecha</th><th style={th}>Aforo</th><th style={th}>Q&A</th></tr>
        </thead>
        <tbody>
          {proyecciones.map(p => (
            <tr key={p.IdProyeccion} style={{ borderBottom: '1px solid #eee' }}>
              <td style={td}>{p.Titulo}</td><td style={td}>{p.NombreSala}</td>
              <td style={td}>{new Date(p.FechaHora).toLocaleString('es-BO')}</td>
              <td style={td}>{p.AforoDisponible}/{p.Capacidad}</td>
              <td style={td}>{p.TieneQA ? 'Sí' : 'No'}</td>
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
