import { useState, useEffect } from 'react'
import api from '../api'

export default function VenderAbono() {
  const [asistentes, setAsistentes] = useState([])
  const [tiposAbono, setTiposAbono] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [form, setForm] = useState({ IdAsistente: '', IdTipoAbono: '', IdEdicion: '', PagoExitoso: true })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.getAsistentes(), fetch('/api/tiposabono').then(r => r.json()), api.getEdiciones()])
      .then(([a, t, e]) => { setAsistentes(a); setTiposAbono(t); setEdiciones(e) })
      .catch(() => {
        api.getAsistentes().then(a => setAsistentes(a))
        fetch('/api/tiposabono').then(r => r.json()).then(t => setTiposAbono(t))
        api.getEdiciones().then(e => setEdiciones(e))
      })
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const res = await api.venderAbono({
        IdAsistente: parseInt(form.IdAsistente),
        IdTipoAbono: parseInt(form.IdTipoAbono),
        IdEdicion: parseInt(form.IdEdicion),
        PagoExitoso: form.PagoExitoso,
      })
      setMsg(res.message)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Vender Abono</h2>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: 500 }}>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Asistente</label>
          <select style={inputStyle} value={form.IdAsistente} onChange={e => setForm({ ...form, IdAsistente: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {asistentes.map(a => <option key={a.IdAsistente} value={a.IdAsistente}>{a.Nombre}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Tipo de Abono</label>
          <select style={inputStyle} value={form.IdTipoAbono} onChange={e => setForm({ ...form, IdTipoAbono: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {tiposAbono.map(t => <option key={t.IdTipoAbono} value={t.IdTipoAbono}>{t.NombreAbono} - Bs. {t.Precio}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Edición</label>
          <select style={inputStyle} value={form.IdEdicion} onChange={e => setForm({ ...form, IdEdicion: e.target.value })} required>
            <option value="">Seleccionar...</option>
            {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, fontWeight: 600 }}>Simular Pago</label>
          <select style={inputStyle} value={String(form.PagoExitoso)} onChange={e => setForm({ ...form, PagoExitoso: e.target.value === 'true' })}>
            <option value="true">Pago Exitoso</option>
            <option value="false">Pago Fallido</option>
          </select>
        </div>
        <button type="submit" style={btnStyle}>Vender Abono</button>
        {msg && <p style={{ color: 'green', marginTop: 8, fontSize: 13 }}>{msg}</p>}
        {error && <p style={{ color: 'red', marginTop: 8, fontSize: 13 }}>{error}</p>}
      </form>
    </div>
  )
}

const inputStyle = { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btnStyle = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
