import { useState, useEffect } from 'react'
import api from '../api'

export default function ComprarEntrada() {
  const [asistentes, setAsistentes] = useState([])
  const [proyecciones, setProyecciones] = useState([])
  const [tarifas, setTarifas] = useState([])
  const [form, setForm] = useState({ IdAsistente: '', IdProyeccion: '', IdTarifa: '' })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.getAsistentes(), api.getProyecciones(), api.getTarifas()])
      .then(([a, p, t]) => { setAsistentes(a); setProyecciones(p); setTarifas(t) })
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const res = await api.comprarEntrada({
        IdAsistente: parseInt(form.IdAsistente),
        IdProyeccion: parseInt(form.IdProyeccion),
        IdTarifa: parseInt(form.IdTarifa),
      })
      setMsg(res.message)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Comprar Entrada</h2>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Asistente</label>
          <select style={inputStyle} value={form.IdAsistente} onChange={e => setForm({ ...form, IdAsistente: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {asistentes.map(a => <option key={a.IdAsistente} value={a.IdAsistente}>{a.Nombre}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Proyección</label>
          <select style={inputStyle} value={form.IdProyeccion} onChange={e => setForm({ ...form, IdProyeccion: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {proyecciones.filter(p => p.AforoDisponible > 0).map(p => (
              <option key={p.IdProyeccion} value={p.IdProyeccion}>{p.Titulo} - {new Date(p.FechaHora).toLocaleString('es-BO')}</option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Tarifa</label>
          <select style={inputStyle} value={form.IdTarifa} onChange={e => setForm({ ...form, IdTarifa: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {tarifas.map(t => <option key={t.IdTarifa} value={t.IdTarifa}>{t.NombreTarifa} - Bs. {t.Precio}</option>)}
          </select>
        </div>
        <button type="submit" style={btnStyle}>Comprar Entrada</button>
        {msg && <p style={{ color: 'green', marginTop: 8, fontSize: 13 }}>{msg}</p>}
        {error && <p style={{ color: 'red', marginTop: 8, fontSize: 13 }}>{error}</p>}
      </form>
    </div>
  )
}

const inputStyle = { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btnStyle = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
