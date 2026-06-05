import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminPersonal() {
  const [personal, setPersonal] = useState([])
  const [peliculas, setPeliculas] = useState([])
  const [roles, setRoles] = useState([])
  const [tab, setTab] = useState('personal')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  // Forms
  const [formP, setFormP] = useState({ Nombre: '', Biografia: '', Email: '', Telefono: '', Nacionalidad: '' })
  const [editingP, setEditingP] = useState(null)
  const [formRol, setFormRol] = useState({ IdPersonal: '', IdPelicula: '', Rol: 'Actor' })

  const loadData = async () => {
    setLoading(true)
    try {
      const [p, pe, r] = await Promise.all([
        api.getPersonal(),
        api.getPeliculas(),
        api.getRoles()
      ])
      setPersonal(p)
      setPeliculas(pe)
      setRoles(r)
    } catch (err) {
      setMsg('Error al cargar datos: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSubmitPersonal = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      if (editingP) {
        await api.updatePersonal(editingP, formP)
        setMsg('Personal actualizado exitosamente')
      } else {
        await api.createPersonal(formP)
        setMsg('Personal registrado exitosamente')
      }
      setFormP({ Nombre: '', Biografia: '', Email: '', Telefono: '', Nacionalidad: '' })
      setEditingP(null)
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleEditPersonal = (p) => {
    setEditingP(p.IdPersonal)
    setFormP({
      Nombre: p.Nombre,
      Biografia: p.Biografia || '',
      Email: p.Email || '',
      Telefono: p.Telefono || '',
      Nacionalidad: p.Nacionalidad || ''
    })
  }

  const handleDeletePersonal = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar a esta persona? Esto desvinculará sus roles, alojamientos y traslados.')) return
    setMsg('')
    try {
      await api.deletePersonal(id)
      setMsg('Personal eliminado exitosamente')
      if (editingP === id) {
        setEditingP(null)
        setFormP({ Nombre: '', Biografia: '', Email: '', Telefono: '', Nacionalidad: '' })
      }
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleSubmitRol = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      await api.createRol({
        IdPersonal: parseInt(formRol.IdPersonal),
        IdPelicula: parseInt(formRol.IdPelicula),
        Rol: formRol.Rol
      })
      setMsg('Rol de película asignado exitosamente')
      setFormRol({ IdPersonal: '', IdPelicula: '', Rol: 'Actor' })
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleDeleteRol = async (personalId, peliculaId, rol) => {
    if (!window.confirm('¿Está seguro de quitar este rol de la película?')) return
    setMsg('')
    try {
      await api.deleteRol(personalId, peliculaId, rol)
      setMsg('Rol de película quitado exitosamente')
      loadData()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Gestión de Personal y Reparto</h2>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <button onClick={() => setTab('personal')} className="btn" style={{ background: tab === 'personal' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', color: '#fff' }}>
          Personal / Artistas
        </button>
        <button onClick={() => setTab('roles')} className="btn" style={{ background: tab === 'roles' ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', color: '#fff' }}>
          Reparto e Integrantes de Películas
        </button>
      </div>

      {loading && <p style={{ color: 'var(--text-secondary)' }}>Cargando datos del festival...</p>}

      {!loading && tab === 'personal' && (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editingP ? 'Editar Personal' : 'Registrar Personal'}</h3>
            <form onSubmit={handleSubmitPersonal}>
              <div className="form-group">
                <label className="form-label">Nombre Completo *</label>
                <input className="input" placeholder="Ej. Javier Torrico" value={formP.Nombre} onChange={e => setFormP({ ...formP, Nombre: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Nacionalidad</label>
                <input className="input" placeholder="Ej. Boliviana" value={formP.Nacionalidad} onChange={e => setFormP({ ...formP, Nacionalidad: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input className="input" type="email" placeholder="Ej. jtorrico@festcine.com" value={formP.Email} onChange={e => setFormP({ ...formP, Email: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Teléfono de Contacto</label>
                <input className="input" placeholder="Ej. +591 76000000" value={formP.Telefono} onChange={e => setFormP({ ...formP, Telefono: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Biografía / Perfil</label>
                <textarea className="textarea" placeholder="Breve trayectoria del director, actor o productor..." rows={3} value={formP.Biografia} onChange={e => setFormP({ ...formP, Biografia: e.target.value })} />
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editingP ? 'Actualizar' : 'Guardar'}</button>
                {editingP && (
                  <button type="button" className="btn btn-secondary" onClick={() => { setEditingP(null); setFormP({ Nombre: '', Biografia: '', Email: '', Telefono: '', Nacionalidad: '' }) }}>
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
                  <th>Nombre</th>
                  <th>Nacionalidad</th>
                  <th>Contacto</th>
                  <th>Biografía</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {personal.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                      No hay registros de personal todavía.
                    </td>
                  </tr>
                ) : (
                  personal.map(p => (
                    <tr key={p.IdPersonal}>
                      <td style={{ fontWeight: 600 }}>{p.Nombre}</td>
                      <td>{p.Nacionalidad || '-'}</td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                        <div>{p.Email}</div>
                        <div>{p.Telefono}</div>
                      </td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={p.Biografia}>
                        {p.Biografia || '-'}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                          <button onClick={() => handleEditPersonal(p)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>Editar</button>
                          <button onClick={() => handleDeletePersonal(p.IdPersonal)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Eliminar</button>
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

      {!loading && tab === 'roles' && (
        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Asignar Rol en Película</h3>
            <form onSubmit={handleSubmitRol}>
              <div className="form-group">
                <label className="form-label">Persona *</label>
                <select className="select" value={formRol.IdPersonal} onChange={e => setFormRol({ ...formRol, IdPersonal: e.target.value })} required>
                  <option value="">Seleccione personal...</option>
                  {personal.map(p => <option key={p.IdPersonal} value={p.IdPersonal}>{p.Nombre} ({p.Nacionalidad || 'Nacionalidad no especificada'})</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Película *</label>
                <select className="select" value={formRol.IdPelicula} onChange={e => setFormRol({ ...formRol, IdPelicula: e.target.value })} required>
                  <option value="">Seleccione película...</option>
                  {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Rol en la Película *</label>
                <select className="select" value={formRol.Rol} onChange={e => setFormRol({ ...formRol, Rol: e.target.value })} required>
                  <option value="Actor">Actor / Actriz</option>
                  <option value="Director">Director / Directora</option>
                  <option value="Guionista">Guionista</option>
                  <option value="Productor">Productor / Productora</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>Asignar Rol</button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Película</th>
                  <th>Integrante</th>
                  <th>Rol Asignado</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                      No hay roles de reparto asignados todavía.
                    </td>
                  </tr>
                ) : (
                  roles.map((r, index) => (
                    <tr key={index}>
                      <td style={{ fontWeight: 600 }}>{r.Pelicula}</td>
                      <td>{r.Personal}</td>
                      <td>
                        <span className={`badge ${
                          r.Rol === 'Director' ? 'badge-premiada' :
                          r.Rol === 'Productor' ? 'badge-seleccionada' :
                          r.Rol === 'Guionista' ? 'badge-postulada' : 'badge-postulada'
                        }`}>
                          {r.Rol}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button onClick={() => handleDeleteRol(r.IdPersonal, r.IdPelicula, r.Rol)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Desvincular</button>
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
