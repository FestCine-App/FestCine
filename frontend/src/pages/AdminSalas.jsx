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
    try { await api.createSede(formSede); setMsg('Sede creada'); setFormSede({ NombreSede: '', Direccion: '', Ciudad: '', SitioWeb: '' }); api.getSedes().then(setSedes) }
    catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearSala = async (e) => {
    e.preventDefault()
    try { await api.createSala({ ...formSala, Capacidad: parseInt(formSala.Capacidad), IdSede: parseInt(formSala.IdSede) }); setMsg('Sala creada'); setFormSala({ NombreSala: '', Capacidad: '', IdSede: '' }); api.getSalas().then(setSalas) }
    catch (err) { setMsg('Error: ' + err.message) }
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Gestión de Sedes y Salas</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 12px', fontSize: 16 }}>Nueva Sede</h3>
          <form onSubmit={crearSede}>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Nombre de la Sede" style={inp} value={formSede.NombreSede} onChange={e => setFormSede({ ...formSede, NombreSede: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Dirección" style={inp} value={formSede.Direccion} onChange={e => setFormSede({ ...formSede, Direccion: e.target.value })} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Ciudad" style={inp} value={formSede.Ciudad} onChange={e => setFormSede({ ...formSede, Ciudad: e.target.value })} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Sitio Web" style={inp} value={formSede.SitioWeb} onChange={e => setFormSede({ ...formSede, SitioWeb: e.target.value })} />
            </div>
            <button type="submit" style={btn}>Crear Sede</button>
          </form>
        </div>

        <div style={{ background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 12px', fontSize: 16 }}>Nueva Sala</h3>
          <form onSubmit={crearSala}>
            <div style={{ marginBottom: 12 }}>
              <select style={inp} value={formSala.IdSede} onChange={e => setFormSala({ ...formSala, IdSede: e.target.value })} required>
                <option value="">Seleccionar Sede</option>
                {sedes.map(s => <option key={s.IdSede} value={s.IdSede}>{s.NombreSede}</option>)}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Nombre de la Sala" style={inp} value={formSala.NombreSala} onChange={e => setFormSala({ ...formSala, NombreSala: e.target.value })} required />
            </div>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Capacidad" type="number" style={inp} value={formSala.Capacidad} onChange={e => setFormSala({ ...formSala, Capacidad: e.target.value })} required />
            </div>
            <button type="submit" style={btn}>Crear Sala</button>
          </form>
        </div>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead style={{ background: '#1a1a2e', color: '#fff' }}>
          <tr><th style={th}>Sala</th><th style={th}>Sede</th><th style={th}>Capacidad</th></tr>
        </thead>
        <tbody>
          {salas.map(s => (
            <tr key={s.IdSala} style={{ borderBottom: '1px solid #eee' }}>
              <td style={td}>{s.NombreSala}</td><td style={td}>{s.NombreSede}</td><td style={td}>{s.Capacidad}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {msg && <p style={{ fontSize: 13, marginTop: 8 }}>{msg}</p>}
    </div>
  )
}

const inp = { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }
const btn = { padding: '10px 20px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: 4, fontSize: 14, fontWeight: 600, cursor: 'pointer' }
const th = { padding: '8px 12px', textAlign: 'left', fontSize: 13 }
const td = { padding: '8px 12px', fontSize: 13 }
