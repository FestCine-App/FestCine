import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminPatrocinadores() {
  const [patrocinadores, setPatrocinadores] = useState([])
  const [patrocinios, setPatrocinios] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [tab, setTab] = useState('patrocinadores')
  const [formP, setFormP] = useState({ NombreEmpresa: '', Contacto: '', Email: '', RedesSociales: '' })
  const [formPE, setFormPE] = useState({ IdPatrocinador: '', IdEdicion: '', TipoAporte: 'Economico', Monto: '', DescripcionAporte: '' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all([api.getPatrocinadores(), api.getPatrocinios(), api.getEdiciones()])
      .then(([p, pe, e]) => { setPatrocinadores(p); setPatrocinios(pe); setEdiciones(e) })
  }, [])

  const crearPatrocinador = async (e) => {
    e.preventDefault()
    try { 
      await api.createPatrocinador(formP)
      setMsg('Patrocinador corporativo registrado exitosamente')
      setFormP({ NombreEmpresa: '', Contacto: '', Email: '', RedesSociales: '' })
      api.getPatrocinadores().then(setPatrocinadores) 
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearPatrocinio = async (e) => {
    e.preventDefault()
    try {
      await api.createPatrocinio({ ...formPE, IdPatrocinador: parseInt(formPE.IdPatrocinador), IdEdicion: parseInt(formPE.IdEdicion), Monto: formPE.Monto ? parseFloat(formPE.Monto) : null })
      setMsg('Aporte de patrocinio registrado exitosamente')
      setFormPE({ IdPatrocinador: '', IdEdicion: '', TipoAporte: 'Economico', Monto: '', DescripcionAporte: '' })
      api.getPatrocinios().then(setPatrocinios)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Patrocinadores y Alianzas Comerciales</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Administre las marcas aliadas y los aportes de financiamiento o canje para las ediciones del festival.
          </p>
        </div>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <button onClick={() => { setTab('patrocinadores'); setMsg(''); }}
          className="btn"
          style={{ 
            background: tab === 'patrocinadores' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', 
            color: '#fff',
            border: tab === 'patrocinadores' ? 'none' : '1px solid rgba(255,255,255,0.08)'
          }}>
          Empresas Patrocinadoras
        </button>
        <button onClick={() => { setTab('patrocinios'); setMsg(''); }}
          className="btn"
          style={{ 
            background: tab === 'patrocinios' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', 
            color: '#fff',
            border: tab === 'patrocinios' ? 'none' : '1px solid rgba(255,255,255,0.08)'
          }}>
          Aportes por Edición
        </button>
      </div>

      {tab === 'patrocinadores' && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Registrar Empresa</h3>
            <form onSubmit={crearPatrocinador}>
              <div className="form-group">
                <label className="form-label">Nombre de Empresa *</label>
                <input placeholder="Ej. Cervecería Boliviana" className="input" value={formP.NombreEmpresa} onChange={e => setFormP({ ...formP, NombreEmpresa: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Persona de Contacto</label>
                <input placeholder="Ej. Carlos Pérez" className="input" value={formP.Contacto} onChange={e => setFormP({ ...formP, Contacto: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Email Corporativo</label>
                <input placeholder="Ej. alianzas@cbn.bo" type="email" className="input" value={formP.Email} onChange={e => setFormP({ ...formP, Email: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Redes Sociales / Website</label>
                <input placeholder="Ej. facebook.com/cbn" className="input" value={formP.RedesSociales} onChange={e => setFormP({ ...formP, RedesSociales: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
                Registrar Patrocinador
              </button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Empresa</th>
                  <th>Contacto Encargado</th>
                  <th>Email</th>
                  <th>Canales Digitales</th>
                </tr>
              </thead>
              <tbody>
                {patrocinadores.length === 0 ? (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No hay patrocinadores registrados.</td></tr>
                ) : (
                  patrocinadores.map(p => (
                    <tr key={p.IdPatrocinador}>
                      <td style={{ fontWeight: 600 }}>{p.NombreEmpresa}</td>
                      <td>{p.Contacto || '-'}</td>
                      <td style={{ fontSize: 13 }}>{p.Email || '-'}</td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{p.RedesSociales || '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'patrocinios' && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Registrar Patrocinio</h3>
            <form onSubmit={crearPatrocinio}>
              <div className="form-group">
                <label className="form-label">Empresa Patrocinadora *</label>
                <select className="select" value={formPE.IdPatrocinador} onChange={e => setFormPE({ ...formPE, IdPatrocinador: e.target.value })} required>
                  <option value="">Seleccione empresa...</option>
                  {patrocinadores.map(p => <option key={p.IdPatrocinador} value={p.IdPatrocinador}>{p.NombreEmpresa}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Edición del Festival *</label>
                <select className="select" value={formPE.IdEdicion} onChange={e => setFormPE({ ...formPE, IdEdicion: e.target.value })} required>
                  <option value="">Seleccione edición...</option>
                  {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Tipo de Aporte *</label>
                <select className="select" value={formPE.TipoAporte} onChange={e => setFormPE({ ...formPE, TipoAporte: e.target.value })}>
                  <option value="Economico">Económico (Dinero)</option>
                  <option value="Especie">Especie (Servicios / Mercancía)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Monto Aportado (Bs.)</label>
                <input placeholder="Ej. 15000" type="number" step="0.01" className="input" value={formPE.Monto} onChange={e => setFormPE({ ...formPE, Monto: e.target.value })} />
              </div>

              <div className="form-group">
                <label className="form-label">Descripción de Canje / Detalle</label>
                <textarea placeholder="Ej. 200 botellas de agua para invitados o detalle del patrocinio..." rows={2} className="textarea" value={formPE.DescripcionAporte} onChange={e => setFormPE({ ...formPE, DescripcionAporte: e.target.value })} />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
                Registrar Patrocinio
              </button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Empresa</th>
                  <th>Edición</th>
                  <th>Tipo Aporte</th>
                  <th>Monto Económico</th>
                  <th>Detalles</th>
                </tr>
              </thead>
              <tbody>
                {patrocinios.length === 0 ? (
                  <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No se registran aportes de patrocinio.</td></tr>
                ) : (
                  patrocinios.map(p => (
                    <tr key={p.IdPatrocinio}>
                      <td style={{ fontWeight: 600 }}>{p.NombreEmpresa}</td>
                      <td>{p.NombreEdicion}</td>
                      <td>
                        <span className={`badge ${p.TipoAporte === 'Economico' ? 'badge-premiada' : 'badge-seleccionada'}`}>
                          {p.TipoAporte === 'Economico' ? 'Económico' : 'Especie'}
                        </span>
                      </td>
                      <td style={{ fontWeight: 600, color: p.Monto ? 'var(--accent-emerald)' : 'var(--text-secondary)' }}>
                        {p.Monto ? `Bs. ${parseFloat(p.Monto).toFixed(2)}` : '-'}
                      </td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={p.DescripcionAporte}>
                        {p.DescripcionAporte || '-'}
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

