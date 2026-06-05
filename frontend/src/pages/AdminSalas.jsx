import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminSalas() {
  const [sedes, setSedes] = useState([])
  const [salas, setSalas] = useState([])
  const [formSede, setFormSede] = useState({ NombreSede: '', Direccion: '', Ciudad: '', SitioWeb: '' })
  const [formSala, setFormSala] = useState({ NombreSala: '', Capacidad: '', IdSede: '' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api.getSedes().then(setSedes)
    api.getSalas().then(setSalas)
  }, [])

  const crearSede = async (e) => {
    e.preventDefault()
    try { 
      await api.createSede(formSede)
      setMsg('Sede del festival creada exitosamente')
      setFormSede({ NombreSede: '', Direccion: '', Ciudad: '', SitioWeb: '' })
      api.getSedes().then(setSedes) 
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearSala = async (e) => {
    e.preventDefault()
    try { 
      await api.createSala({ ...formSala, Capacidad: parseInt(formSala.Capacidad), IdSede: parseInt(formSala.IdSede) })
      setMsg('Sala de proyección creada exitosamente')
      setFormSala({ NombreSala: '', Capacidad: '', IdSede: '' })
      api.getSalas().then(setSalas) 
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Gestión de Sedes y Salas</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Configure las salas de cine y las sedes físicas que albergan las proyecciones del festival.
          </p>
        </div>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24, marginBottom: 24 }}>
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>Nueva Sede</h3>
          <form onSubmit={crearSede}>
            <div className="form-group">
              <label className="form-label">Nombre de Sede *</label>
              <input placeholder="Ej. Multicine Santa Cruz" className="input" value={formSede.NombreSede} onChange={e => setFormSede({ ...formSede, NombreSede: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Dirección</label>
              <input placeholder="Ej. Av. Las Américas 450" className="input" value={formSede.Direccion} onChange={e => setFormSede({ ...formSede, Direccion: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Ciudad</label>
              <input placeholder="Ej. Santa Cruz" className="input" value={formSede.Ciudad} onChange={e => setFormSede({ ...formSede, Ciudad: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Sitio Web / URL Sede</label>
              <input placeholder="Ej. www.multicine.com.bo" className="input" value={formSede.SitioWeb} onChange={e => setFormSede({ ...formSede, SitioWeb: e.target.value })} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>Crear Sede</button>
          </form>
        </div>

        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>Nueva Sala</h3>
          <form onSubmit={crearSala}>
            <div className="form-group">
              <label className="form-label">Sede de Ubicación *</label>
              <select className="select" value={formSala.IdSede} onChange={e => setFormSala({ ...formSala, IdSede: e.target.value })} required>
                <option value="">Seleccionar Sede...</option>
                {sedes.map(s => <option key={s.IdSede} value={s.IdSede}>{s.NombreSede} ({s.Ciudad || 'Ciudad no especificada'})</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Nombre de la Sala *</label>
              <input placeholder="Ej. Sala 1 - IMAX" className="input" value={formSala.NombreSala} onChange={e => setFormSala({ ...formSala, NombreSala: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Capacidad de Espectadores *</label>
              <input placeholder="Ej. 180" type="number" className="input" value={formSala.Capacidad} onChange={e => setFormSala({ ...formSala, Capacidad: e.target.value })} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>Crear Sala</button>
          </form>
        </div>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Sala de Cine</th>
              <th>Sede Ubicación</th>
              <th>Dirección de Sede</th>
              <th style={{ textAlign: 'right' }}>Capacidad Sala</th>
            </tr>
          </thead>
          <tbody>
            {salas.length === 0 ? (
              <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No se registran salas programadas.</td></tr>
            ) : (
              salas.map(s => (
                <tr key={s.IdSala}>
                  <td style={{ fontWeight: 600 }}>{s.NombreSala}</td>
                  <td>{s.NombreSede}</td>
                  <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                    {sedes.find(se => se.NombreSede === s.NombreSede)?.Direccion || 'Dirección no especificada'}
                  </td>
                  <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--accent-pink)' }}>{s.Capacidad} personas</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

