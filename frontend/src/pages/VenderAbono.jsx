import { useState, useEffect } from 'react'
import api from '../api'

export default function VenderAbono() {
  const [asistentes, setAsistentes] = useState([])
  const [tiposAbono, setTiposAbono] = useState([])
  const [form, setForm] = useState({ IdAsistente: '', IdTipoAbono: '', PagoExitoso: true })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    Promise.all([api.getAsistentes(), api.getTiposAbono()])
      .then(([a, t]) => { 
        setAsistentes(a)
        setTiposAbono(t)
      })
      .catch((err) => {
        setError('Error al cargar datos necesarios: ' + err.message)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const res = await api.venderAbono({
        IdAsistente: parseInt(form.IdAsistente),
        IdTipoAbono: parseInt(form.IdTipoAbono),
        PagoExitoso: form.PagoExitoso,
      })
      setMsg(res.message || 'Abono adquirido con éxito')
      setForm({ IdAsistente: '', IdTipoAbono: '', PagoExitoso: true })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: 600, margin: '0 auto' }}>
      <div style={{ marginBottom: 24, textAlign: 'center' }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, margin: '0 0 8px 0', background: 'linear-gradient(135deg, #fff 30%, var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Venta de Abonos
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>
          Emita pases de acceso general (Fin de Semana o Total) para una edición del festival.
        </p>
      </div>

      <div className="glass-card">
        {loading && <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>Cargando información del sistema...</p>}

        {!loading && (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Asistente Registrado *</label>
              <select className="select" value={form.IdAsistente} onChange={e => setForm({ ...form, IdAsistente: e.target.value })} required>
                <option value="">Seleccione el asistente...</option>
                {asistentes.map(a => (
                  <option key={a.IdAsistente} value={a.IdAsistente}>
                    {a.Nombre} ({a.TipoAsistente})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Tipo de Abono *</label>
              <select className="select" value={form.IdTipoAbono} onChange={e => setForm({ ...form, IdTipoAbono: e.target.value })} required>
                <option value="">Seleccione el tipo de abono...</option>
                {tiposAbono.map(t => (
                  <option key={t.IdTipoAbono} value={t.IdTipoAbono}>
                    {t.NombreAbono} — Bs. {parseFloat(t.Precio).toFixed(2)} ({t.Descripcion || 'Acceso general'})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Pasarela de Pago (Simulación) *</label>
              <select className="select" value={String(form.PagoExitoso)} onChange={e => setForm({ ...form, PagoExitoso: e.target.value === 'true' })}>
                <option value="true">Pago Aprobado (Procesar Abono)</option>
                <option value="false">Pago Rechazado (Forzar Fallo y Rollback)</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 16, height: 48, fontSize: 16 }}>
              Procesar y Emitir Abono
            </button>
          </form>
        )}

        {msg && (
          <div style={{ marginTop: 20, padding: 16, background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 10, color: '#34d399', fontSize: 14, fontWeight: 500, textAlign: 'center' }}>
            ✓ {msg}
          </div>
        )}
        {error && (
          <div style={{ marginTop: 20, padding: 16, background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 10, color: '#fb7185', fontSize: 14, fontWeight: 500, textAlign: 'center' }}>
            ✗ Error: {error}
          </div>
        )}
      </div>
    </div>
  )
}

