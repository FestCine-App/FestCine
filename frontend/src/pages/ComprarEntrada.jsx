import { useState, useEffect } from 'react'
import api from '../api'

export default function ComprarEntrada() {
  const [asistentes, setAsistentes] = useState([])
  const [proyecciones, setProyecciones] = useState([])
  const [eventos, setEventos] = useState([])
  const [tarifas, setTarifas] = useState([])
  
  const [ticketType, setTicketType] = useState('cine') // 'cine' or 'evento'
  const [form, setForm] = useState({ IdAsistente: '', IdProyeccion: '', IdEvento: '', IdTarifa: '' })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    Promise.all([
      api.getAsistentes(),
      api.getProyecciones(),
      api.getEventos(),
      api.getTarifas()
    ]).then(([a, p, e, t]) => {
      setAsistentes(a)
      setProyecciones(p)
      setEventos(e)
      setTarifas(t)
    }).catch(err => {
      setError('Error al cargar datos del festival: ' + err.message)
    })
  }, [])

  const handleTypeChange = (type) => {
    setTicketType(type)
    setForm(prev => ({
      ...prev,
      IdProyeccion: '',
      IdEvento: ''
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg('')
    setError('')
    setLoading(true)

    try {
      const payload = {
        IdAsistente: parseInt(form.IdAsistente),
        IdTarifa: parseInt(form.IdTarifa)
      }

      if (ticketType === 'cine') {
        if (!form.IdProyeccion) {
          setError('Por favor seleccione una proyección cinematográfica.')
          setLoading(false)
          return
        }
        payload.IdProyeccion = parseInt(form.IdProyeccion)
      } else {
        if (!form.IdEvento) {
          setError('Por favor seleccione un evento paralelo.')
          setLoading(false)
          return
        }
        payload.IdEvento = parseInt(form.IdEvento)
      }

      const res = await api.comprarEntrada(payload)
      setMsg(res.message)
      setForm({ IdAsistente: '', IdProyeccion: '', IdEvento: '', IdTarifa: '' })
      
      // Reload screenings to update aforo
      api.getProyecciones().then(setProyecciones)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 450px', gap: 32, alignItems: 'start', maxWidth: 1000, margin: '0 auto' }}>
      <div>
        <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Adquirir Entrada</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Compra de boletos individuales válidos para una proyección cinematográfica o el acceso a un evento paralelo especial.
        </p>

        {/* Toggle ticket type */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 12,
          padding: 6,
          marginBottom: 24
        }}>
          <button type="button" onClick={() => handleTypeChange('cine')} style={{
            padding: '12px',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 700,
            fontSize: 14,
            transition: 'all 0.2s',
            background: ticketType === 'cine' ? 'var(--accent-purple)' : 'transparent',
            color: '#fff'
          }}>
            Función de Cine
          </button>
          <button type="button" onClick={() => handleTypeChange('evento')} style={{
            padding: '12px',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 700,
            fontSize: 14,
            transition: 'all 0.2s',
            background: ticketType === 'evento' ? 'var(--accent-purple)' : 'transparent',
            color: '#fff'
          }}>
            Evento Especial (Taller/Masterclass)
          </button>
        </div>

        <form onSubmit={handleSubmit} className="glass-card">
          <div className="form-group">
            <label className="form-label">Asistente Registrado *</label>
            <select className="select" value={form.IdAsistente} onChange={e => setForm({ ...form, IdAsistente: e.target.value })} required>
              <option value="">Seleccione asistente...</option>
              {asistentes.map(a => <option key={a.IdAsistente} value={a.IdAsistente}>{a.Nombre} ({a.TipoAsistente})</option>)}
            </select>
          </div>

          {ticketType === 'cine' ? (
            <div className="form-group">
              <label className="form-label">Proyección Cinematográfica *</label>
              <select className="select" value={form.IdProyeccion} onChange={e => setForm({ ...form, IdProyeccion: e.target.value })} required>
                <option value="">Seleccione función...</option>
                {proyecciones.filter(p => p.AforoDisponible > 0).map(p => (
                  <option key={p.IdProyeccion} value={p.IdProyeccion}>
                    {p.Titulo} — {p.NombreSede} / {p.NombreSala} ({new Date(p.FechaHora).toLocaleString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}) · [Aforo: {p.AforoDisponible}]
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div className="form-group">
              <label className="form-label">Evento Paralelo / Taller *</label>
              <select className="select" value={form.IdEvento} onChange={e => setForm({ ...form, IdEvento: e.target.value })} required>
                <option value="">Seleccione evento...</option>
                {eventos.map(ev => (
                  <option key={ev.IdEvento} value={ev.IdEvento}>
                    [{ev.TipoEvento}] {ev.NombreEvento} — Costo: Bs. {ev.CostoInscripcion} ({new Date(ev.FechaHora).toLocaleString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Tarifa de Boleto *</label>
            <select className="select" value={form.IdTarifa} onChange={e => setForm({ ...form, IdTarifa: e.target.value })} required>
              <option value="">Seleccione tarifa...</option>
              {tarifas.map(t => <option key={t.IdTarifa} value={t.IdTarifa}>{t.NombreTarifa} — Bs. {parseFloat(t.Precio).toFixed(2)}</option>)}
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: 14, fontSize: 16, marginTop: 16 }} disabled={loading}>
            {loading ? 'Procesando registro...' : 'Confirmar Adquisición'}
          </button>
        </form>
      </div>

      {/* Ticket visualization / Status sidebar */}
      <div>
        <h3 style={{ fontSize: 18, marginBottom: 16 }}>Estado de Operación</h3>
        
        {/* Error Notification */}
        {error && (
          <div className="glass-card animate-scale-in" style={{ borderColor: 'var(--accent-rose)', background: 'rgba(244, 63, 94, 0.08)', marginBottom: 20 }}>
            <h4 style={{ color: 'var(--accent-rose)', fontSize: 14, fontWeight: 700, marginBottom: 6 }}>Error en Operación</h4>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>{error}</p>
          </div>
        )}

        {/* Success Ticket View */}
        {msg && (
          <div className="glass-card animate-scale-in" style={{
            borderColor: 'var(--accent-emerald)',
            background: 'rgba(16, 185, 129, 0.06)',
            padding: 0,
            overflow: 'hidden'
          }}>
            <div style={{
              background: 'linear-gradient(135deg, var(--accent-emerald), #047857)',
              padding: '16px 20px',
              color: '#fff',
              fontWeight: 800,
              fontSize: 14,
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              ✓ Boleto Emitido
            </div>
            
            <div style={{ padding: 20 }}>
              <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>
                {msg}
              </p>
              
              <div style={{
                borderTop: '2px dashed rgba(255, 255, 255, 0.1)',
                margin: '16px 0',
                position: 'relative'
              }}>
                <div style={{ position: 'absolute', left: -28, top: -10, width: 16, height: 16, borderRadius: '50%', background: 'var(--bg-primary)' }}></div>
                <div style={{ position: 'absolute', right: -28, top: -10, width: 16, height: 16, borderRadius: '50%', background: 'var(--bg-primary)' }}></div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 12, color: 'var(--text-secondary)' }}>
                <div>
                  <span style={{ display: 'block', fontSize: 10, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Fecha Compra</span>
                  <strong style={{ color: '#fff' }}>{new Date().toLocaleDateString('es-ES')}</strong>
                </div>
                <div>
                  <span style={{ display: 'block', fontSize: 10, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Tipo Entrada</span>
                  <strong style={{ color: '#fff' }}>{ticketType === 'cine' ? 'CINE' : 'EVENTO'}</strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {!msg && !error && (
          <div className="glass-card" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: 48, marginBottom: 12, opacity: 0.5 }}>🎟</div>
            <p style={{ fontSize: 14, margin: 0 }}>Completa el formulario para registrar y emitir un boleto de acceso.</p>
          </div>
        )}
      </div>
    </div>
  )
}
