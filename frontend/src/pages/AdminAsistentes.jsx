import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminAsistentes() {
  const [asistentes, setAsistentes] = useState([])
  const [entradas, setEntradas] = useState([])
  const [abonos, setAbonos] = useState([])
  const [form, setForm] = useState({ Nombre: '', Email: '', Telefono: '', TipoAsistente: 'General' })
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState('All')
  const [selectedAsistente, setSelectedAsistente] = useState(null)
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const [asis, ent, ab] = await Promise.all([
        api.getAsistentes(),
        api.getEntradas(),
        api.getAbonos()
      ])
      setAsistentes(asis)
      setEntradas(ent)
      setAbonos(ab)
    } catch (err) {
      setMsg('Error al cargar asistentes: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      await api.createAsistente(form)
      setMsg('Asistente registrado con éxito')
      setForm({ Nombre: '', Email: '', Telefono: '', TipoAsistente: 'General' })
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  // Filter assistants
  const filteredAsistentes = asistentes.filter(a => {
    const matchesSearch = a.Nombre.toLowerCase().includes(search.toLowerCase()) || a.Email.toLowerCase().includes(search.toLowerCase())
    const matchesType = filterType === 'All' || a.TipoAsistente === filterType
    return matchesSearch && matchesType
  })

  // Get details for selected assistant
  const getAsistenteDetails = (asistente) => {
    const asisEntradas = entradas.filter(e => e.IdAsistente === asistente.IdAsistente)
    const asisAbonos = abonos.filter(a => a.IdAsistente === asistente.IdAsistente)
    setSelectedAsistente({ ...asistente, entradas: asisEntradas, abonos: asisAbonos })
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Asistentes y Abonos Vendidos</h2>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 24, alignItems: 'start' }}>
        {/* Register assistant form */}
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>Registrar Asistente</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nombre Completo *</label>
              <input className="input" placeholder="Ej. Ana Gomez" value={form.Nombre} onChange={e => setForm({ ...form, Nombre: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Correo Electrónico *</label>
              <input className="input" type="email" placeholder="Ej. agomez@gmail.com" value={form.Email} onChange={e => setForm({ ...form, Email: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Teléfono</label>
              <input className="input" placeholder="Ej. 72000000" value={form.Telefono} onChange={e => setForm({ ...form, Telefono: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Categoría / Tipo de Acreditación *</label>
              <select className="select" value={form.TipoAsistente} onChange={e => setForm({ ...form, TipoAsistente: e.target.value })} required>
                <option value="General">Público General</option>
                <option value="Prensa">Prensa / Medios</option>
                <option value="Industria">Cineasta / Industria</option>
                <option value="VIP">Invitado VIP</option>
                <option value="Jurado">Jurado del Festival</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>Registrar Asistente</button>
          </form>
        </div>

        {/* List of assistants */}
        <div>
          <div className="glass-card" style={{ padding: 16, marginBottom: 20, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <input className="input" placeholder="Buscar asistente por nombre o email..." value={search} onChange={e => setSearch(e.target.value)} style={{ flex: 1, minWidth: 200 }} />
            <select className="select" value={filterType} onChange={e => setFilterType(e.target.value)} style={{ width: 200 }}>
              <option value="All">Todos los Tipos</option>
              <option value="General">General</option>
              <option value="Prensa">Prensa</option>
              <option value="Industria">Industria</option>
              <option value="VIP">VIP</option>
              <option value="Jurado">Jurado</option>
            </select>
          </div>

          {loading && <p style={{ color: 'var(--text-secondary)' }}>Cargando asistentes del festival...</p>}

          {!loading && (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Tipo</th>
                    <th style={{ textAlign: 'right' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAsistentes.length === 0 ? (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                        No se encontraron asistentes con los filtros seleccionados.
                      </td>
                    </tr>
                  ) : (
                    filteredAsistentes.map(a => (
                      <tr key={a.IdAsistente}>
                        <td style={{ fontWeight: 600 }}>{a.Nombre}</td>
                        <td>{a.Email}</td>
                        <td>
                          <span className={`badge ${
                            a.TipoAsistente === 'VIP' ? 'badge-premiada' :
                            a.TipoAsistente === 'Jurado' ? 'badge-seleccionada' :
                            a.TipoAsistente === 'Industria' ? 'badge-postulada' : 'badge-secondary'
                          }`} style={a.TipoAsistente === 'Prensa' ? { background: 'rgba(217, 70, 239, 0.15)', color: '#d946ef', border: '1px solid rgba(217, 70, 239, 0.2)' } : {}}>
                            {a.TipoAsistente}
                          </span>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button onClick={() => getAsistenteDetails(a)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>
                            Ver Compras y Abonos
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Details overlay modal */}
      {selectedAsistente && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: 20 }} onClick={() => setSelectedAsistente(null)}>
          <div className="glass-card animate-scale-in" style={{ width: '100%', maxWidth: 700, maxHeight: '90vh', overflowY: 'auto', background: 'var(--bg-secondary)', border: '1px solid rgba(255, 255, 255, 0.1)' }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 12 }}>
              <div>
                <h3 style={{ fontSize: 22, fontWeight: 800 }}>Detalle de Asistente</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>{selectedAsistente.Nombre} ({selectedAsistente.TipoAsistente})</p>
              </div>
              <button className="btn btn-secondary" onClick={() => setSelectedAsistente(null)} style={{ padding: '8px 12px' }}>Cerrar</button>
            </div>

            <h4 style={{ fontSize: 16, marginBottom: 12, color: 'var(--accent-pink)' }}>Abonos del Festival</h4>
            {selectedAsistente.abonos.length === 0 ? (
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 24 }}>Este asistente no cuenta con abonos acreditados.</p>
            ) : (
              <div className="table-container" style={{ marginBottom: 24 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Abono</th>
                      <th>Edición</th>
                      <th>Código</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedAsistente.abonos.map(ab => (
                      <tr key={ab.IdAbono}>
                        <td style={{ fontWeight: 600 }}>{ab.NombreAbono}</td>
                        <td>{ab.NombreEdicion}</td>
                        <td style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--accent-purple)' }}>{ab.CodigoAcceso}</td>
                        <td>
                          <span className={`badge ${ab.Pagado ? 'badge-premiada' : 'badge-rechazada'}`}>
                            {ab.Pagado ? 'PAGADO' : 'PENDIENTE'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <h4 style={{ fontSize: 16, marginBottom: 12, color: 'var(--accent-pink)' }}>Entradas Adquiridas</h4>
            {selectedAsistente.entradas.length === 0 ? (
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>Este asistente no ha comprado entradas individuales.</p>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Tipo</th>
                      <th>Función / Evento</th>
                      <th>Fecha y Hora</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedAsistente.entradas.map(ent => (
                      <tr key={ent.IdEntrada}>
                        <td>
                          <span className="badge badge-secondary" style={ent.IdEvento ? { background: 'rgba(219, 70, 239, 0.15)', color: '#d946ef', border: '1px solid rgba(219, 70, 239, 0.2)' } : {}}>
                            {ent.IdEvento ? 'EVENTO' : 'CINE'}
                          </span>
                        </td>
                        <td style={{ fontWeight: 600 }}>
                          {ent.IdEvento ? (
                            `Evento: ${ent.Pelicula || 'Evento Paralelo'}`  // Note: ent.Pelicula or corresponding event title is fetched
                          ) : (
                            `Proyección: ${ent.Pelicula}`
                          )}
                        </td>
                        <td style={{ fontSize: 13 }}>{new Date(ent.FechaHora).toLocaleString('es-ES')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
