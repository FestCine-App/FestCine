import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminLogistica() {
  const [personal, setPersonal] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [hoteles, setHoteles] = useState([])
  const [alojamientos, setAlojamientos] = useState([])
  const [traslados, setTraslados] = useState([])
  const [tab, setTab] = useState('hoteles')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  // Forms
  const [formHotel, setFormHotel] = useState({ NombreHotel: '', Direccion: '', Estrellas: '5' })
  const [editingHotel, setEditingHotel] = useState(null)

  const [formAloj, setFormAloj] = useState({ IdPersonal: '', IdHotel: '', NroHabitacion: '', CheckIn: '', CheckOut: '' })
  const [editingAloj, setEditingAloj] = useState(null)

  const [formTraslado, setFormTraslado] = useState({ IdPersonal: '', TipoTraslado: 'Vuelo', Origen: '', Destino: '', FechaHora: '', NroVuelo: '' })
  const [editingTraslado, setEditingTraslado] = useState(null)

  const loadData = async () => {
    setLoading(true)
    try {
      const [p, ed, h, al, tr] = await Promise.all([
        api.getPersonal(),
        api.getEdiciones(),
        api.getHoteles(),
        api.getAlojamientos(),
        api.getTraslados()
      ])
      setPersonal(p)
      setEdiciones(ed)
      setHoteles(h)
      setAlojamientos(al)
      setTraslados(tr)
    } catch (err) {
      setMsg('Error al cargar datos logísticos: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // --- HOTELES CRUD ---
  const handleSubmitHotel = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      const payload = { ...formHotel, Estrellas: parseInt(formHotel.Estrellas) }
      if (editingHotel) {
        await api.updateHotel(editingHotel, payload)
        setMsg('Hotel actualizado con éxito')
      } else {
        await api.createHotel(payload)
        setMsg('Hotel registrado con éxito')
      }
      setFormHotel({ NombreHotel: '', Direccion: '', Estrellas: '5' })
      setEditingHotel(null)
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleEditHotel = (h) => {
    setEditingHotel(h.IdHotel)
    setFormHotel({ NombreHotel: h.NombreHotel, Direccion: h.Direccion || '', Estrellas: String(h.Estrellas) })
  }

  const handleDeleteHotel = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar este hotel? Esto eliminará todos los alojamientos vinculados.')) return
    setMsg('')
    try {
      await api.deleteHotel(id)
      setMsg('Hotel eliminado')
      if (editingHotel === id) {
        setEditingHotel(null)
        setFormHotel({ NombreHotel: '', Direccion: '', Estrellas: '5' })
      }
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  // --- ALOJAMIENTOS CRUD ---
  const handleSubmitAloj = async (e) => {
    e.preventDefault()
    setMsg('')

    if (new Date(formAloj.CheckOut) <= new Date(formAloj.CheckIn)) {
      setMsg('Error: La fecha de Check-Out debe ser posterior a la de Check-In.')
      return
    }

    try {
      const payload = {
        IdPersonal: parseInt(formAloj.IdPersonal),
        IdHotel: parseInt(formAloj.IdHotel),
        NroHabitacion: formAloj.NroHabitacion,
        CheckIn: formAloj.CheckIn,
        CheckOut: formAloj.CheckOut
      }
      if (editingAloj) {
        await api.updateAlojamiento(editingAloj, payload)
        setMsg('Alojamiento actualizado')
      } else {
        await api.createAlojamiento(payload)
        setMsg('Hospedaje registrado')
      }
      setFormAloj({ IdPersonal: '', IdHotel: '', NroHabitacion: '', CheckIn: '', CheckOut: '' })
      setEditingAloj(null)
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleEditAloj = (al) => {
    setEditingAloj(al.IdAlojamiento)
    setFormAloj({
      IdPersonal: String(al.IdPersonal),
      IdHotel: String(al.IdHotel),
      NroHabitacion: al.NroHabitacion,
      CheckIn: al.CheckIn,
      CheckOut: al.CheckOut
    })
  }

  const handleDeleteAloj = async (id) => {
    if (!window.confirm('¿Desea eliminar este registro de hospedaje?')) return
    setMsg('')
    try {
      await api.deleteAlojamiento(id)
      setMsg('Registro de hospedaje eliminado')
      if (editingAloj === id) {
        setEditingAloj(null)
        setFormAloj({ IdPersonal: '', IdHotel: '', NroHabitacion: '', CheckIn: '', CheckOut: '' })
      }
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  // --- TRASLADOS CRUD ---
  const handleSubmitTraslado = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      const payload = {
        IdPersonal: parseInt(formTraslado.IdPersonal),
        TipoTraslado: formTraslado.TipoTraslado,
        Origen: formTraslado.Origen,
        Destino: formTraslado.Destino,
        FechaHora: formTraslado.FechaHora.replace('T', ' '),
        NroVuelo: formTraslado.NroVuelo || null
      }
      if (editingTraslado) {
        await api.updateTraslado(editingTraslado, payload)
        setMsg('Traslado actualizado')
      } else {
        await api.createTraslado(payload)
        setMsg('Traslado registrado')
      }
      setFormTraslado({ IdPersonal: '', TipoTraslado: 'Vuelo', Origen: '', Destino: '', FechaHora: '', NroVuelo: '' })
      setEditingTraslado(null)
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleEditTraslado = (tr) => {
    setEditingTraslado(tr.IdTraslado)
    setFormTraslado({
      IdPersonal: String(tr.IdPersonal),
      TipoTraslado: tr.TipoTraslado,
      Origen: tr.Origen,
      Destino: tr.Destino,
      FechaHora: tr.FechaHora ? tr.FechaHora.substring(0, 16).replace(' ', 'T') : '',
      NroVuelo: tr.NroVuelo || ''
    })
  }

  const handleDeleteTraslado = async (id) => {
    if (!window.confirm('¿Desea eliminar este traslado?')) return
    setMsg('')
    try {
      await api.deleteTraslado(id)
      setMsg('Traslado eliminado')
      if (editingTraslado === id) {
        setEditingTraslado(null)
        setFormTraslado({ IdPersonal: '', TipoTraslado: 'Vuelo', Origen: '', Destino: '', FechaHora: '', NroVuelo: '' })
      }
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Logística e Invitados</h2>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <button onClick={() => setTab('hoteles')} className="btn" style={{ background: tab === 'hoteles' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', color: '#fff' }}>
          Hoteles
        </button>
        <button onClick={() => setTab('alojamientos')} className="btn" style={{ background: tab === 'alojamientos' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', color: '#fff' }}>
          Hospedajes (Alojamientos)
        </button>
        <button onClick={() => setTab('traslados')} className="btn" style={{ background: tab === 'traslados' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', color: '#fff' }}>
          Traslados (Transporte)
        </button>
      </div>

      {loading && <p style={{ color: 'var(--text-secondary)' }}>Cargando información logística...</p>}

      {/* --- TAB HOTELES --- */}
      {!loading && tab === 'hoteles' && (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editingHotel ? 'Editar Hotel' : 'Registrar Hotel'}</h3>
            <form onSubmit={handleSubmitHotel}>
              <div className="form-group">
                <label className="form-label">Nombre del Hotel *</label>
                <input className="input" placeholder="Ej. Hotel Camino Real" value={formHotel.NombreHotel} onChange={e => setFormHotel({ ...formHotel, NombreHotel: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Dirección</label>
                <input className="input" placeholder="Ej. Av. San Martín 123" value={formHotel.Direccion} onChange={e => setFormHotel({ ...formHotel, Direccion: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Categoría (Estrellas) *</label>
                <select className="select" value={formHotel.Estrellas} onChange={e => setFormHotel({ ...formHotel, Estrellas: e.target.value })} required>
                  <option value="5">5 Estrellas</option>
                  <option value="4">4 Estrellas</option>
                  <option value="3">3 Estrellas</option>
                  <option value="2">2 Estrellas</option>
                  <option value="1">1 Estrella</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingHotel ? 'Actualizar' : 'Guardar'}</button>
                {editingHotel && (
                  <button type="button" className="btn btn-secondary" onClick={() => { setEditingHotel(null); setFormHotel({ NombreHotel: '', Direccion: '', Estrellas: '5' }) }}>
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre Hotel</th>
                  <th>Dirección</th>
                  <th>Estrellas</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {hoteles.map(h => (
                  <tr key={h.IdHotel}>
                    <td style={{ fontWeight: 600 }}>{h.NombreHotel}</td>
                    <td>{h.Direccion || '-'}</td>
                    <td style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>{'★'.repeat(h.Estrellas)}</td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                        <button onClick={() => handleEditHotel(h)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>Editar</button>
                        <button onClick={() => handleDeleteHotel(h.IdHotel)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Eliminar</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* --- TAB ALOJAMIENTOS --- */}
      {!loading && tab === 'alojamientos' && (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editingAloj ? 'Editar Hospedaje' : 'Hospedar Invitado'}</h3>
            <form onSubmit={handleSubmitAloj}>
              <div className="form-group">
                <label className="form-label">Invitado (Personal) *</label>
                <select className="select" value={formAloj.IdPersonal} onChange={e => setFormAloj({ ...formAloj, IdPersonal: e.target.value })} required>
                  <option value="">Seleccione invitado...</option>
                  {personal.map(p => <option key={p.IdPersonal} value={p.IdPersonal}>{p.Nombre} ({p.Nacionalidad || 'Nacionalidad N/A'})</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Hotel *</label>
                <select className="select" value={formAloj.IdHotel} onChange={e => setFormAloj({ ...formAloj, IdHotel: e.target.value })} required>
                  <option value="">Seleccione hotel...</option>
                  {hoteles.map(h => <option key={h.IdHotel} value={h.IdHotel}>{h.NombreHotel} ({'★'.repeat(h.Estrellas)})</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Nro de Habitación *</label>
                <input className="input" placeholder="Ej. 302" value={formAloj.NroHabitacion} onChange={e => setFormAloj({ ...formAloj, NroHabitacion: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Fecha Check-In *</label>
                <input className="input" type="date" value={formAloj.CheckIn} onChange={e => setFormAloj({ ...formAloj, CheckIn: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Fecha Check-Out *</label>
                <input className="input" type="date" value={formAloj.CheckOut} onChange={e => setFormAloj({ ...formAloj, CheckOut: e.target.value })} required />
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingAloj ? 'Actualizar' : 'Hospedar'}</button>
                {editingAloj && (
                  <button type="button" className="btn btn-secondary" onClick={() => { setEditingAloj(null); setFormAloj({ IdPersonal: '', IdHotel: '', NroHabitacion: '', CheckIn: '', CheckOut: '' }) }}>
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Invitado</th>
                  <th>Hotel</th>
                  <th>Habitación</th>
                  <th>Fechas (Check-in/out)</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {alojamientos.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>No hay hospedajes registrados.</td>
                  </tr>
                ) : (
                  alojamientos.map(al => (
                    <tr key={al.IdAlojamiento}>
                      <td style={{ fontWeight: 600 }}>{al.Personal}</td>
                      <td>{al.NombreHotel}</td>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>Hab. {al.NroHabitacion}</td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                        {new Date(al.CheckIn).toLocaleDateString('es-ES', { timeZone: 'UTC' })} al {new Date(al.CheckOut).toLocaleDateString('es-ES', { timeZone: 'UTC' })}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                          <button onClick={() => handleEditAloj(al)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>Editar</button>
                          <button onClick={() => handleDeleteAloj(al.IdAlojamiento)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Eliminar</button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* --- TAB TRASLADOS --- */}
      {!loading && tab === 'traslados' && (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editingTraslado ? 'Editar Traslado' : 'Registrar Traslado'}</h3>
            <form onSubmit={handleSubmitTraslado}>
              <div className="form-group">
                <label className="form-label">Invitado (Personal) *</label>
                <select className="select" value={formTraslado.IdPersonal} onChange={e => setFormTraslado({ ...formTraslado, IdPersonal: e.target.value })} required>
                  <option value="">Seleccione invitado...</option>
                  {personal.map(p => <option key={p.IdPersonal} value={p.IdPersonal}>{p.Nombre}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Tipo de Traslado *</label>
                <select className="select" value={formTraslado.TipoTraslado} onChange={e => setFormTraslado({ ...formTraslado, TipoTraslado: e.target.value })} required>
                  <option value="Vuelo">Vuelo Internacional / Nacional</option>
                  <option value="Transfer">Transfer Terrestre (Hotel/Aeropuerto)</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Origen *</label>
                <input className="input" placeholder="Ej. Lima (LIM) o Aeropuerto VVI" value={formTraslado.Origen} onChange={e => setFormTraslado({ ...formTraslado, Origen: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Destino *</label>
                <input className="input" placeholder="Ej. Santa Cruz (VVI) o Hotel Tajibos" value={formTraslado.Destino} onChange={e => setFormTraslado({ ...formTraslado, Destino: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Fecha y Hora *</label>
                <input className="input" type="datetime-local" value={formTraslado.FechaHora} onChange={e => setFormTraslado({ ...formTraslado, FechaHora: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Nro de Vuelo (opcional)</label>
                <input className="input" placeholder="Ej. OB-102 o LA-240" value={formTraslado.NroVuelo} onChange={e => setFormTraslado({ ...formTraslado, NroVuelo: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingTraslado ? 'Actualizar' : 'Guardar'}</button>
                {editingTraslado && (
                  <button type="button" className="btn btn-secondary" onClick={() => { setEditingTraslado(null); setFormTraslado({ IdPersonal: '', TipoTraslado: 'Vuelo', Origen: '', Destino: '', FechaHora: '', NroVuelo: '' }) }}>
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Invitado</th>
                  <th>Tipo</th>
                  <th>Origen ➔ Destino</th>
                  <th>Fecha y Hora</th>
                  <th>Nro Vuelo</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {traslados.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>No hay traslados programados.</td>
                  </tr>
                ) : (
                  traslados.map(tr => (
                    <tr key={tr.IdTraslado}>
                      <td style={{ fontWeight: 600 }}>{tr.Personal}</td>
                      <td>
                        <span className={`badge ${tr.TipoTraslado === 'Vuelo' ? 'badge-seleccionada' : 'badge-postulada'}`}>
                          {tr.TipoTraslado}
                        </span>
                      </td>
                      <td style={{ fontWeight: 600, fontSize: 13 }}>{tr.Origen} ➔ {tr.Destino}</td>
                      <td style={{ fontSize: 13 }}>{new Date(tr.FechaHora).toLocaleString('es-ES')}</td>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{tr.NroVuelo || '-'}</td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                          <button onClick={() => handleEditTraslado(tr)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>Editar</button>
                          <button onClick={() => handleDeleteTraslado(tr.IdTraslado)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Eliminar</button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
